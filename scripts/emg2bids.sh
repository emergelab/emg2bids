INPUT_DIR="/Volumes/Titan/jaewon/EMGBCM" # base directory for all subjects
OUTPUT_DIR="/Volumes/Titan/jaewon/EMGBCM_bids" # output dir
LOG_DIR="${OUTPUT_DIR}/logs"
HEURISTIC="../emg2bids.py"
HEUDICONV_OPTS="-g all -c dcm2niix --bids --overwrite -o ${OUTPUT_DIR} -f ${HEURISTIC}"

mkdir -p $LOG_DIR

N=6

task(){
    scan_dir="$1"

    if [[ $scan_dir =~ "exclude" ]]; then # check if dir has exclude tag
        return
    fi

    subject="${scan_dir##*/}"
    cmd="heudiconv $HEUDICONV_OPTS -s ${subject} --files ${scan_dir}/dicom/raw.sc/*"
    $cmd >> "${LOG_DIR}/${subject}.txt"
}

for scan_dir in $INPUT_DIR/*;
do
    ((i=i%N)); ((i++==0)) && wait
    task $scan_dir &
done