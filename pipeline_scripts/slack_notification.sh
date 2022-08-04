#!/bin/bash

function slack_payload() {

    if [[ "${EXIT_STATUS}" == "${FAILURE}" ]]; then
        T1=$((echo "cat <<EOF" ; cat pipeline_scripts/failure.json)| sh )
        message_set=true

    elif [[ "${EXIT_STATUS}" == "${SUCCESS}" ]] && [[ ${FAIL_ONLY} == 'false' ]]; then
        T1=$((echo "cat <<EOF" ; cat pipeline_scripts/success.json)| sh | )
        message_set=true
    fi

    SLACK_MSG_BODY=$T1
}

function runner_status() {
        SLACK_MSG_BODY=$((echo "cat <<EOF" ; cat pipeline_scripts/runner.json)| sh | )
        message_set=true
}

function send_notification() {

    FAILURE=1
    SUCCESS=0
    FAIL_ONLY=false
    DISABLED=false
    RUNNER_STATUS=false
    message_set=false

    SLACK_WEBHOOK=$1
    export SLACK_CHANNEL=$2
    EXIT_STATUS=$(cat .job_status)

    for i in "$@" ; do
        if [[ $i == "FAIL_ONLY" ]] ; then
            FAIL_ONLY=true
        fi
        if [[ $i == "DISABLED" ]] ; then
            DISABLED=true
        fi
        if [[ $i == "RUNNER" ]] ; then
            RUNNER_STATUS=true
        fi
    done

    echo $DISABLED

    if [[ ${DISABLED} == 'false' ]];then
        slack_payload
    elif [[ ${RUNNER_STATUS} == 'true' ]];then
        export OFFLINE_RUNNERS=$(curl --header "JOB-TOKEN: $CI_JOB_TOKEN" "https://gitlab-tooling.dsp.intdigital.ee.co.uk//api/v4/runners?status=offline&tag_list=aws-android-runner,aws-mac-runner"  | jq '.[] | .description' | paste -sd, -)
        runner_status
    fi

    if [[ ${message_set} == 'true' ]];then
        curl -X POST "${SLACK_WEBHOOK}" -H "Content-type: application/json" -d "${SLACK_MSG_BODY}"
    fi

}

"$@"
