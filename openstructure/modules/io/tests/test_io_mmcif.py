import os
import unittest
import subprocess
import ost
from ost import *

class TestMMCifInfo(unittest.TestCase):
  def setUp(self):
    pass

  def test_mmcifinfo_citation(self):
    c = io.MMCifInfoCitation()
    # test ID setting/ getting
    c.SetID('ID')
    self.assertEqual(c.GetID(), 'ID')
    # test CAS setting/ getting
    c.SetCAS('FOO')
    self.assertEqual(c.GetCAS(), 'FOO')
    # test ISBN setting/ getting
    c.SetISBN('0-0-0-0-0-0')
    self.assertEqual(c.GetISBN(), '0-0-0-0-0-0')
    # test published_in setting/ getting
    c.SetPublishedIn('Best Book Ever')
    self.assertEqual(c.GetPublishedIn(), 'Best Book Ever')
    # test volume setting/ getting
    c.SetVolume('3')
    self.assertEqual(c.GetVolume(), '3')
    # test page setting/ getting
    c.SetPageFirst('1')
    self.assertEqual(c.GetPageFirst(), '1')
    c.SetPageLast('10')
    self.assertEqual(c.GetPageLast(), '10')
    # test doi setting/ getting
    c.SetDOI('HERE')
    self.assertEqual(c.GetDOI(), 'HERE')
    # test PubMed setting/ getting
    c.SetPubMed(815)
    self.assertEqual(c.GetPubMed(), 815)
    # test year setting/ getting
    c.SetYear(815)
    self.assertEqual(c.GetYear(), 815)
    # test title setting/ getting
    c.SetTitle('Foo')
    self.assertEqual(c.GetTitle(), 'Foo')
    # test book_publisher set & get
    c.SetBookPublisher("Hugo")
    self.assertEqual(c.GetBookPublisher(), "Hugo")
    # test book_publisher_city set & get
    c.SetBookPublisherCity("Basel")
    self.assertEqual(c.book_publisher_city, "Basel")
    # test citation type
    self.assertTrue(c.IsCitationTypeUnknown())
    self.assertEqual(c.citation_type, io.MMCifInfoCType.Unknown)
    # test auhtors setting/ getting
    s = ost.StringList()
    s.append('Foo')
    c.SetAuthorList(s)
    s2 = c.GetAuthorList()
    self.assertEqual(s2[0], 'Foo')

    i = io.MMCifInfo()
    i.SetMethod('Deep-Fry')
    i.SetResolution(2.0)
    i.SetEMResolution(3.0)
    i.AddCitation(c)
    s.append('Bar')
    i.AddAuthorsToCitation('ID', s)

    cl = i.GetCitations()
    self.assertEqual(len(cl), 1)
    al = cl[0].GetAuthorList()
    self.assertEqual(len(al), 2)
    self.assertEqual(al[0], 'Foo')
    self.assertEqual(al[1], 'Bar')

    self.assertEqual(i.GetMethod(), 'Deep-Fry')
    self.assertEqual(i.GetResolution(), 2.0)
    self.assertEqual(i.GetEMResolution(), 3.0)


  def test_mmcifinfo_biounit(self):
    b = io.MMCifInfoBioUnit()
    b.SetDetails('Details')
    b.SetMethodDetails('MethodDetails')
    self.assertEqual(b.GetDetails(), 'Details')
    self.assertEqual(b.GetMethodDetails(), 'MethodDetails')
    b.method_details = 'AttrMethodDetails'
    self.assertEqual(b.method_details, 'AttrMethodDetails')
    b.AddChain('A')
    b.AddChain('B')
    cl = b.GetChainList()
    il = b.GetChainIntervalList()
    self.assertEqual(cl[0], 'A')
    self.assertEqual(il[0][0], 0)
    self.assertEqual(il[0][1], 2)
    s = ost.StringList()
    s.append('B')
    s.append('C')
    s.append('D')
    b.SetChainList(s)
    cl = b.GetChainList()
    il = b.GetChainIntervalList()
    self.assertEqual(il[0][0], 0)
    self.assertEqual(il[0][1], 3)
    self.assertEqual(cl[0], 'B')
    self.assertEqual(cl[1], 'C')
    self.assertEqual(cl[2], 'D')

    i = io.MMCifInfo()
    i.AddBioUnit(b)
    i.AddBioUnit(b)
    b.SetID("2")
    i.AddBioUnit(b)

    bl = i.GetBioUnits()
    il = bl[0].GetChainIntervalList()
    self.assertEqual(il[0][0], 0)
    self.assertEqual(il[0][1], 3)
    self.assertEqual(il[1][0], 3)
    self.assertEqual(il[1][1], 6)
    self.assertEqual(len(bl), 2)


  def test_mmcifinfo_transoperation(self):
    o = io.MMCifInfoTransOp()
    o.SetID("1")
    self.assertEqual(o.GetID(), '1')
    o.SetType("identity operation")
    self.assertEqual(o.GetType(), 'identity operation')
    o.SetVector(1.0, 2.0, 3.0)
    self.assertEqual(o.GetVector().x, 1.0)
    self.assertEqual(o.GetVector().y, 2.0)
    self.assertEqual(o.GetVector().z, 3.0)
    o.SetMatrix(1, 2, 3, 4, 5, 6, 7, 8, 9)
    self.assertEqual(geom.Equal(o.GetMatrix(),
                                 geom.Mat3(1, 2, 3, 4, 5, 6, 7, 8, 9)), True)

    i = io.MMCifInfo()
    i.AddOperation(o)
    ol = i.GetOperations()
    self.assertEqual(ol[0].GetID(), '1')

    b = io.MMCifInfoBioUnit()
    b.AddOperations(ol)
    oll = b.GetOperations()
    self.assertEqual(oll[0][0].GetID(), '1')
    tr_ol = b.GetOperationsIntervalList()
    self.assertEqual(len(tr_ol), 1)
    self.assertEqual(tr_ol[0][0], 0)
    self.assertEqual(tr_ol[0][1], 1)

  def test_mmcifinfo_biounit_pdbize_with_multiple_transforms(self):
    ent, seqres, info = io.LoadMMCIF("testfiles/mmcif/multiple_transforms.cif.gz",
                                     seqres=True,
                                     info=True)
    pdb_ent = info.GetBioUnits()[0].PDBize(ent)
    chains = pdb_ent.chains
    self.assertEqual(''.join([c.name for c in chains]), 
                      'A_-BCD')
    ligand_chain = chains[1]
    ligand_residues = ligand_chain.residues
    self.assertEqual([r.number for r in ligand_residues],
                      [mol.ResNum(1), mol.ResNum(2), mol.ResNum(3), mol.ResNum(4)])

  def test_mmcifinfo_biounit_pdbize(self):
    ent, seqres, info = io.LoadMMCIF("testfiles/mmcif/3T6C.cif.gz",
                                     seqres=True,
                                     info=True)
    pdb_ent = info.GetBioUnits()[0].PDBize(ent)
    pdb_seqres_ent = info.GetBioUnits()[0].PDBize(ent, seqres)

    self.assertEqual(''.join([c.name for c in pdb_ent.chains]),
                      'AB_-CDEFGH')
    self.assertEqual([c.residue_count for c in pdb_ent.chains],
                      [415, 414, 64, 3816, 415, 414, 415, 414, 415, 414])
    self.assertEqual([c.atom_count for c in pdb_ent.chains],
                      [3231, 3223, 268, 3816, 3231, 3223, 3231, 3223, 3231, 3223])
    self.assertEqual([c.GetBondCount() for c in pdb_ent.chains],
                      [3311, 3303, 204, 0, 3311, 3303, 3311, 3303, 3311, 3303])

    self.assertEqual(''.join([c.name for c in pdb_seqres_ent.chains]),
                      ''.join([c.name for c in pdb_ent.chains]))
    self.assertEqual([c.residue_count for c in pdb_seqres_ent.chains],
                      [c.residue_count for c in pdb_ent.chains])
    self.assertEqual([c.atom_count for c in pdb_seqres_ent.chains],
                      [c.atom_count for c in pdb_ent.chains])
    self.assertEqual([c.GetBondCount() for c in pdb_seqres_ent.chains],
                      [c.GetBondCount() for c in pdb_ent.chains])

  def test_mmcifinfo_biounit_pdbize_transformation(self):
    ent, seqres, info = io.LoadMMCIF("testfiles/mmcif/3hqv.cif.gz",
                                     seqres=True,
                                     info=True)
    pdb_ent, t = info.GetBioUnits()[0].PDBize(ent, transformation=True)
    self.assertAlmostEqual(pdb_ent.GetCenterOfAtoms()[0], -915.759, 1)
    self.assertAlmostEqual(pdb_ent.GetCenterOfAtoms()[1], -952.345, 1)
    self.assertAlmostEqual(pdb_ent.GetCenterOfAtoms()[2], 3221.75, 1)
    self.assertEqual(geom.Equal(t,
                                 geom.Mat4(1,0,0,-920.462,
                                           0,1,0,-966.654,
                                           0,0,1,1703,
                                           0,0,0,1),
                                 epsilon=0.01), True)

  def test_mmcifinfo_structdetails(self):
    d = io.MMCifInfoStructDetails()

    d.SetEntryID('1BAR')
    d.SetTitle('A Title')
    d.SetCASPFlag('N')
    d.SetDescriptor('FooBar')
    d.SetMass(1.0)
    d.SetMassMethod('Good Guess')
    d.SetModelDetails('Created with SwissModel')
    d.SetModelTypeDetails('Average')
    self.assertEqual(d.GetEntryID(), '1BAR')
    self.assertEqual(d.GetTitle(), 'A Title')
    self.assertEqual(d.GetCASPFlag(), 'N')
    self.assertEqual(d.GetDescriptor(), 'FooBar')
    self.assertEqual(d.GetMass(), 1.0)
    self.assertEqual(d.GetMassMethod(), 'Good Guess')
    self.assertEqual(d.GetModelDetails(), 'Created with SwissModel')  
    self.assertEqual(d.GetModelTypeDetails(), 'Average') 

    i = io.MMCifInfo()
    i.SetStructDetails(d)
    self.assertEqual(i.GetStructDetails().GetEntryID(), '1BAR')
    self.assertEqual(i.GetStructDetails().GetTitle(), 'A Title')
    self.assertEqual(i.GetStructDetails().GetCASPFlag(), 'N')
    self.assertEqual(i.GetStructDetails().GetDescriptor(), 'FooBar')
    self.assertEqual(i.GetStructDetails().GetMass(), 1.0)
    self.assertEqual(i.GetStructDetails().GetMassMethod(), 'Good Guess')
    self.assertEqual(i.GetStructDetails().GetModelDetails(),
                      'Created with SwissModel')
    self.assertEqual(i.GetStructDetails().GetModelTypeDetails(), 'Average')

  def test_mmcifinfo_obsolete(self):
    obs = io.MMCifInfoObsolete()
    obs.SetDate('2011-08-31')
    obs.SetID('SPRSDE')
    obs.SetPDBID('1FOO')
    obs.SetReplacedPDBID('2BAR')
    self.assertEqual(obs.GetDate(), '2011-08-31')
    self.assertEqual(obs.GetID(), 'Supersede')
    self.assertEqual(obs.GetPDBID(), '1FOO')
    self.assertEqual(obs.GetReplacedPDBID(), '2BAR')

    i = io.MMCifInfo()
    obs.id = 'OBSLTE'
    i.SetObsoleteInfo(obs)
    self.assertEqual(i.GetObsoleteInfo().GetDate(), '2011-08-31')
    self.assertEqual(i.GetObsoleteInfo().GetID(), 'Obsolete')
    self.assertEqual(i.GetObsoleteInfo().GetPDBID(), '1FOO')
    self.assertEqual(i.GetObsoleteInfo().GetReplacedPDBID(), '2BAR')

  def test_remote_loading(self):

    if subprocess.call(['ping google.com -c 1'], shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
      print("No internet connection (or wrong OS) to test remote loading in "
            "io.LoadMMCIF: ignoring unit test")
      return

    # let's hope that crambin stays the same forever
    crambin_pdb = io.LoadMMCIF('1crn', remote=True)
    self.assertEqual(len(crambin_pdb.residues), 46)
    self.assertEqual(len(crambin_pdb.atoms), 327)

  def test_mmcifinfo_entitybranch(self):
    # test MMCifInfoEntityBranchLink

    info = io.MMCifInfo()
    info.AddEntityBranchLink("A", 42, 43, "O3", "C4", 2)
    info.AddEntityBranchLink("B", 142, 143, "XXO3", "XXC4", 3)
    info.AddEntityBranchLink("B", 1142, 1143, "XXXXO3", "XXXXC4", 5)

    self.assertEqual(len(info.GetEntityBranchChainNames()), 2)
    self.assertEqual(len(info.GetEntityBranchByChain("A")), 1)
    self.assertEqual(len(info.GetEntityBranchByChain("B")), 2)
    self.assertEqual(len(info.GetEntityBranchByChain("X")), 0) 

    self.assertEqual(info.GetEntityBranchByChain("A")[0].rnum1, 42)
    self.assertEqual(info.GetEntityBranchByChain("A")[0].rnum2, 43)
    self.assertEqual(info.GetEntityBranchByChain("A")[0].aname1, "O3")
    self.assertEqual(info.GetEntityBranchByChain("A")[0].aname2, "C4")
    self.assertEqual(info.GetEntityBranchByChain("A")[0].bond_order, 2)

    self.assertEqual(info.GetEntityBranchByChain("B")[0].rnum1, 142);
    self.assertEqual(info.GetEntityBranchByChain("B")[0].rnum2, 143);
    self.assertEqual(info.GetEntityBranchByChain("B")[0].aname1, "XXO3");
    self.assertEqual(info.GetEntityBranchByChain("B")[0].aname2, "XXC4");
    self.assertEqual(info.GetEntityBranchByChain("B")[0].bond_order, 3);

    self.assertEqual(info.GetEntityBranchByChain("B")[1].rnum1, 1142)
    self.assertEqual(info.GetEntityBranchByChain("B")[1].rnum2, 1143)
    self.assertEqual(info.GetEntityBranchByChain("B")[1].aname1, "XXXXO3")
    self.assertEqual(info.GetEntityBranchByChain("B")[1].aname2, "XXXXC4")
    self.assertEqual(info.GetEntityBranchByChain("B")[1].bond_order, 5)

  def test_mmcif_connect_branch_links(self):

    p = os.path.join("testfiles", "mmcif", "154L.cif")
    ent = mol.CreateEntity()
    reader = io.MMCifReader(p, ent, io.profiles['STRICT'])
    reader.Parse()

    # there are two branch links specified and they should be connected
    # in reader.Parse()
    bonds = ent.bonds
    self.assertEqual(len(bonds), 2)

    # first branch link manually parsed from cif file
    r1 = ent.FindResidue("B", mol.ResNum(2))
    a1 = r1.FindAtom("C1")
    r2 = ent.FindResidue("B", mol.ResNum(1))
    a2 = r2.FindAtom("O4")

    self.assertTrue(mol.BondExists(a1, a2))

    # second branch link manually parsed from cif file
    r1 = ent.FindResidue("B", mol.ResNum(3))
    a1 = r1.FindAtom("C1")
    r2 = ent.FindResidue("B", mol.ResNum(2))
    a2 = r2.FindAtom("O4")

    self.assertTrue(mol.BondExists(a1, a2))


  def test_mmcif_fault_tolerant_citation(self):

    p = os.path.join("testfiles", "mmcif", "AF-A0A024L8A3-F1-model_v4.cif.gz")
    with self.assertRaises(Exception):
      ent, seqres, info = io.LoadMMCIF(p, seqres=True, info=True)
    ent, seqres, info = io.LoadMMCIF(p, seqres=True, info=True,
                                     fault_tolerant=True)


if __name__== '__main__':
  from ost import testutils
  testutils.RunTests()


