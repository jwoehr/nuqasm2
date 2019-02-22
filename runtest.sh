# runtest.sh ... run some regression tests for nuqasm2

LASTVER=$1

if [ "$LASTVER" == "" ]
then
	echo "Usage: $0 LASTVER"
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
for i in yiqing.qasm test_qasm/g*.qasm test_qasm/if.qasm
do
	FNAME=`basename $i .qasm`
	python nuqasm2.py -o test_qasm/out/${FNAME}.out.txt -p --save_source --perf_filepath test_qasm/out/${FNAME}.perf.out.txt $i

done

# run erroneous files
for i in test_qasm/err/*.qasm
do
	FNAME=`basename $i .qasm`
	python nuqasm2.py -o test_qasm/err/out/${FNAME}.out.txt --save_source $i 2>test_qasm/err/out/${FNAME}.err.txt 
done

cd test_qasm/out
diffout

cd ../err/out
diffout


# end
