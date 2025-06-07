#!/bin/bash

echo "Running client-related tests from list..."

while IFS= read -r testfile
do
  echo "Running tests in $testfile"
  pytest "$testfile"
done < client_tests_list.txt

echo "Client tests completed."
