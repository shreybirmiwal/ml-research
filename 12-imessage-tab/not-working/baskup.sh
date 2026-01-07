#!/bin/sh
BACKUP_DIR=./backup

function select_rows () {
  sqlite3 ~/Library/Messages/chat.db "$1"
}

for line in $(select_rows "select distinct guid from chat;" ); do

  contact=$line
  arrIN=(${contact//;/ })
  contactNumber=${arrIN[2]}

  select_rows "
  select is_from_me,text, datetime((date/1000000000) + strftime('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') as date from message where handle_id=(
  select handle_id from chat_handle_join where chat_id=(
  select ROWID from chat where guid='$line')
  )" | sed 's/1\|/Me: /g;s/0\|/Friend: /g' > $BACKUP_DIR/$contactNumber/$line.txt

done