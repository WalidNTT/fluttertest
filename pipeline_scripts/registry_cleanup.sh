#!/bin/bash

PROJECT_TOKEN=$1
CI_PROJECT_ID=$2
CI_API_V4_URL=$3
CURRENT_BRANCH_REG=$4

if [ -z ${CI_COMMIT_TAG+x} ]
  then
    echo "removing $CURRENT_BRANCH_REG"
    delete_url=$(curl -s --header "PRIVATE-TOKEN: $PROJECT_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages?per_page=100" | jq --arg branch "$CURRENT_BRANCH_REG" '.[] | select(.name==$branch) | ._links.delete_api_path')
    delete_url_without_quotes=$(echo $delete_url | sed 's/"//g')

    if [[ $delete_url != "" ]]
      then
          curl --request DELETE --header "PRIVATE-TOKEN: $PROJECT_TOKEN" ${delete_url_without_quotes}
    fi
fi

for branch in $(curl -s --header "PRIVATE-TOKEN: $PROJECT_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages?per_page=100" | jq '.[] | .name' | grep -v ^'"main' | grep -v ^'"release')
  do
    branch_without_quotes=$(echo $branch | sed 's/"//g')
    if [[ $(curl -s --header "PRIVATE-TOKEN: $PROJECT_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests?state=opened&per_page=100" | jq '.[] | .source_branch' | sed 's|/|_|g') =~ "$branch" ]]
       then
           echo "$branch exists"
            else
                 delete_url=$(curl -s --header "PRIVATE-TOKEN: $PROJECT_TOKEN" "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages?per_page=100" | jq --arg branch "$branch_without_quotes" '.[] | select(.name==$branch) | ._links.delete_api_path')
                 delete_url_without_quotes=$(echo $delete_url | sed 's/"//g')
                 curl --request DELETE --header "PRIVATE-TOKEN: $PROJECT_TOKEN" ${delete_url_without_quotes}
                 echo "deleted $branch packages from registry"
    fi
  done
