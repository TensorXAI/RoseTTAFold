import torch
import torch.nn as nn
import torch.nn.functional as F
from Transformer import LayerNorm, SequenceWeight

import torch_geometric
from torch_geometric.data import Data
from torch_geometric.nn import TransformerConv
from utils.utils_mps_fallback import fallback_to_cpu_if_mps

def get_seqsep(idx):
    '''
    Input:
        - idx: residue indices of given sequence (B,L)
    Output:
        - seqsep: sequence separation feature with sign (B, L, L, 1)
                  Sergey found that having sign in seqsep features helps a little
    '''
    seqsep = idx[:,None,:] - idx[:,:,None]
    sign = torch.sign(seqsep)
    seqsep = torch.log(torch.abs(seqsep) + 1.0)
    seqsep = torch.clamp(seqsep, 0.0, 5.5)
    seqsep = sign * seqsep
    return seqsep.unsqueeze(-1)

def make_graph(node, idx, emb):
    ''' create torch_geometric graph from Trunk outputs '''
    fallback = fallback_to_cpu_if_mps(emb.device)
    B, L = emb.shape[:2]

    # |i-j| <= kmin (connect sequentially adjacent residues)
    sep = idx[:,None,:] - idx[:,:,None]
    sep = sep.abs()
    # b, i, j = torch.where(sep > 0)
    b, i, j = tuple(idx.to(fallback) for idx in torch.where(sep > 0))
    
    src = b*L+i
    tgt = b*L+j

    # x = node.reshape(B*L, -1)
    x = node.reshape(B*L, -1).to(fallback)

    G = Data(x=x, 
             edge_index=torch.stack([src,tgt]),
             edge_attr=emb[b,i,j].to(fallback))

    return G

class UniMPBlock(nn.Module):
    '''https://arxiv.org/pdf/2009.03509.pdf'''
    def __init__(self, 
                 node_dim=64,
                 edge_dim=64,
                 heads=4, 
                 dropout=0.15):
        super(UniMPBlock, self).__init__()
        
        self.TConv = TransformerConv(node_dim, node_dim, heads, dropout=dropout, edge_dim=edge_dim)
        self.LNorm = LayerNorm(node_dim*heads)
        self.Linear = nn.Linear(node_dim*heads, node_dim)
        self.Activ = nn.ELU(inplace=True)

    # @torch.cuda.amp.autocast(enabled=True)
    from utils.utils_decorators import cuda_amp_autocast
    @cuda_amp_autocast(enabled=True)
    def forward(self, G):
        xin, e_idx, e_attr = G.x, G.edge_index, G.edge_attr
        x = self.TConv(xin, e_idx, e_attr)
        x = self.LNorm(x)
        x = self.Linear(x)
        out = self.Activ(x+xin)
        return Data(x=out, edge_index=e_idx, edge_attr=e_attr)


class InitStr_Network(nn.Module):
    def __init__(self, 
                 node_dim_in=64, 
                 node_dim_hidden=64,
                 edge_dim_in=128, 
                 edge_dim_hidden=64, 
                 nheads=4, 
                 nblocks=3, 
                 dropout=0.1):
        super(InitStr_Network, self).__init__()

        # embedding layers for node and edge features
        self.norm_node = LayerNorm(node_dim_in)
        self.norm_edge = LayerNorm(edge_dim_in)
        self.encoder_seq = SequenceWeight(node_dim_in, 1, dropout=dropout)

        self.embed_x = nn.Sequential(nn.Linear(node_dim_in+21, node_dim_hidden), nn.ELU(inplace=True))
        self.embed_e = nn.Sequential(nn.Linear(edge_dim_in+1, edge_dim_hidden), nn.ELU(inplace=True))
        
        # graph transformer
        blocks = [UniMPBlock(node_dim_hidden,edge_dim_hidden,nheads,dropout) for _ in range(nblocks)]
        self.transformer = nn.Sequential(*blocks)
        
        # outputs
        self.get_xyz = nn.Linear(node_dim_hidden,9)
    
    def forward(self, seq1hot, idx, msa, pair):
        # Move computations to the CPU if the current device is MPS, 
        # # as certain layers (e.g., DGL or Torch Geometric layers) 
        # # may not fully support MPS. This ensures compatibility.
        device = next(self.parameters()).device
        fallback = fallback_to_cpu_if_mps(device)
        B, N, L = msa.shape[:3]
        msa = self.norm_node(msa)
        pair = self.norm_edge(pair)
        
        w_seq = self.encoder_seq(msa).reshape(B, L, 1, N).permute(0,3,1,2)
        msa = w_seq*msa
        msa = msa.sum(dim=1)
        node = torch.cat((msa, seq1hot), dim=-1)
        node = self.embed_x(node)

        seqsep = get_seqsep(idx) 
        pair = torch.cat((pair, seqsep), dim=-1)
        pair = self.embed_e(pair)
        
        # for name, param in self.transformer.named_parameters():
        #    print(name, param.device) 
        G = make_graph(node, idx, pair)
        # self.transformer.to(torch.device('cpu'))
                
        # for name, param in self.transformer.named_parameters():
        #    print(name, param.device) 
            
        Gout = self.transformer.to(fallback)(G)
        
        xyz = self.get_xyz(Gout.x.to(device))

        return xyz.reshape(B, L, 3, 3) #torch.cat([xyz,node_emb],dim=-1)
