#!/bin/bash

# DATADIR="$CONDA_PREFIX/share/psipred_4.01/data"
# echo $DATADIR

i_a3m="$1"
o_ss="$2"

ID=$(basename $i_a3m .a3m).tmp

$PIPEDIR/csblast-2.2.3/bin/csbuild -i $i_a3m -I a3m -D $PIPEDIR/csblast-2.2.3/data/K4000.crf -o $WDIR/$ID.chk -O chk

head -n 2 $i_a3m > $WDIR/$ID.fasta
echo $ID.chk > $WDIR/$ID.pn
echo $ID.fasta > $WDIR/$ID.sn

# Define the container's directory to mount
CONTAINER_DATA_DIR="/data"

# Run the Docker container with the volume mount and execute the commands
docker run --platform linux/amd64 --rm \
    -v "$WDIR:$CONTAINER_DATA_DIR" \
    -w "$CONTAINER_DATA_DIR" \
    -e ID="$ID" -e i_a3m=$(basename $i_a3m) \
    biox-linux-64 bash -c "
    echo \$CONDA_PREFIX &&
    export BLASTMAT=\$CONDA_PREFIX/data &&
    export DATADIR=\$CONDA_PREFIX/share/psipred_4.01/data &&
    echo \$BLASTMAT &&
    echo \$DATADIR &&
    makemat -P \$ID &&
    psipred \$ID.mtx \$DATADIR/weights.dat \$DATADIR/weights.dat2 \$DATADIR/weights.dat3 > \$ID.ss &&
    psipass2 \$DATADIR/weights_p2.dat 1 1.0 1.0 \$i_a3m.csb.hhblits.ss2 \$ID.ss > \$ID.horiz
"
# makemat -P $ID
# psipred $ID.mtx $DATADIR/weights.dat $DATADIR/weights.dat2 $DATADIR/weights.dat3 > $ID.ss
# psipass2 $DATADIR/weights_p2.dat 1 1.0 1.0 $i_a3m.csb.hhblits.ss2 $ID.ss > $ID.horiz

(
echo ">ss_pred"
grep "^Pred" "$WDIR/$ID.horiz" | awk '{print $2}'
echo ">ss_conf"
grep "^Conf" "$WDIR/$ID.horiz" | awk '{print $2}'
) | awk '{if(substr($1,1,1)==">") {print "\n"$1} else {printf "%s", $1}} END {print ""}' | sed "1d" > $o_ss

rm ${i_a3m}.csb.hhblits.ss2
rm $WDIR/$ID.*
