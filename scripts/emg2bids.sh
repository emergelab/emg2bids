# Set path depending on machine. PIG=Linux; iMAC=Darwin
machine="$(uname)"
if [[ $machine =~ "Linux" ]]; then
    INPUT_DIR="/mnt/t/EMGBCM" # base directory for all subjects
    OUTPUT_DIR="/mnt/t/EMGBCM_bids" # output dir
elif [[ $machine =~ "Darwin" ]]; then
    INPUT_DIR="/Volumes/Titan/jaewon/EMGBCM" # base directory for all subjects
    OUTPUT_DIR="/Volumes/Titan/jaewon/EMGBCM_bids" # output dir
fi

LOG_DIR="${OUTPUT_DIR}/logs"
HEURISTIC="../emg2bids.py"
HEUDICONV_OPTS="-g all -c dcm2niix --bids --overwrite -o ${OUTPUT_DIR} -f ${HEURISTIC}"

mkdir -p $LOG_DIR

for scan_dir in $INPUT_DIR/*;
do
    subject="${scan_dir##*/}"
    
    # check if dir has exclude tag
    if [[ $scan_dir =~ "exclude" ]]; then 
        continue
    # check if output subject already exists; if yes, then skip
    elif [[ -d "${OUTPUT_DIR}/sub-${subject}" ]]; then
        continue
    else
        cmd="heudiconv $HEUDICONV_OPTS -s ${subject} --files ${scan_dir}/dicom/raw.sc/*"
        $cmd >> "${LOG_DIR}/${subject}.txt"
    fi

done