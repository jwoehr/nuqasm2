# runtest.sh ... run some regression tests for nuqasm2

LASTVER=$1
INCPATH=$2

if [ "$LASTVER" == "" ]
then
	echo "Usage: $0 LASTVER INCPATH"
	exit 1
fi

function diffout () {
	echo "# ####################" >outdiff.txt
	echo "# diffs from $LASTVER" >>outdiff.txt
	echo "#" `date '+%Y-%h-%d %H:%M:%S'` >>outdiff.txt
	echo "# ####################" >>outdiff.txt
	echo  >>outdiff.txt
	
	for i in *.out.txt
	do
		echo "# ####################" >>outdiff.txt
		echo "#" $i >>outdiff.txt
		echo "# ####################" >>outdiff.txt
		diff -u $i ${LASTVER}/$i >>outdiff.txt
	done
}

# run 'good' files
for i in yiqing.qasm test_qasm/g*.qasm \
	test_qasm/if.qasm \
	test_qasm/entangled_registers.qasm test_qasm/plaquette_check.qasm
do
	FNAME=`basename $i .qasm`
	nuqasm2 -i $INCPATH -o test_qasm/out/${FNAME}.out.txt -p --save_source -u --perf_filepath test_qasm/out/${FNAME}.perf.out.txt $i

done

# run erroneous files
for i in test_qasm/err/*.qasm
do
	FNAME=`basename $i .qasm`
	nuqasm2 -i $INCPATH -o test_qasm/err/out/${FNAME}.out.txt --save_source -u $i 2>test_qasm/err/out/${FNAME}.err.txt 
done

cd test_qasm/out
diffout

cd ../err/out
diffout


# end
