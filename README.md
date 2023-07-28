VM 서버 관리용 app 모음
mysql_lib.py : app들이 db 쿼리를 하기 위한 라이브러리
update_vm_status.py: 주기적으로 vm 상태를 조회하여 db에 업데이트
vm_utils: vm 정보 조회에 사용되는 라이브러리
그 외 추가 작업 중

20230404
띄어쓰기 및 vm name에 제한이 없는 상황에서 vm name을 추출하는 로직 변경
예외 vm의 경우 vm name 뒤에 서버 ip 맨 뒤자리 추가 해야함 ex) name-203

20230612
ESXi server의 memory 사용률이 90%가 넘으면 momory 사용량 top3 VM 중지