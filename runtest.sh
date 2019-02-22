# runtest.sh ... run some regression tests for nuqasm2
LASTVER=$1
if [ "$LASTVER" == "" ]
then
	echo "Usage: $0 LASTVER"
	exit 1
fi
for i in test_qasm/g*.qasm test_qasm/if.qasm
do
	FNAME=`basename $i .qasm`
	python nuqasm2.py -o test_qasm/out/${FNAME}.out.txt -p --save_source --perf_filepath test_qasm/out/${FNAME}.perf.out.txt $i

done
cd test_qasm/out
echo -n >outdiff.txt
for i in *.out.txt
do
	echo $i >>outdiff.txt
	echo "..." >>outdiff.txt
	diff -c $i ${LASTVER}/$i >>outdiff.txt
done
# end
