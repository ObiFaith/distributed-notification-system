#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

host_name=$(echo $host | cut -d: -f1)
host_port=$(echo $host | cut -d: -f2)

until nc -z $host_name $host_port; do
  echo "Waiting for $host..."
  sleep 1
done

echo "$host is up - executing command"
exec $cmd