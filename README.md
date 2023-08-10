## VM 서버 관리용 app
### 모듈 설명
---
*mysql_lib*: app들이 db 쿼리를 하기 위한 라이브러리 
*manage_vm_app*: 주기적으로 vm 및 ESXi 서버 상태를 조회하여 db에 업데이트
*vm_utils*: vm 정보 조회에 사용되는 라이브러리
*socket_server*: manage web에서 on/off 명령을 받아 ESXi 서버에 on/off 동작 수행
*log_config*: 로그를 남기기 위한 로그 인스턴스 생성 클래스 (singleton 패턴)
---
#### 주요 패치
1) vm name 분류 추가
띄어쓰기 및 vm name에 제한이 없는 상황에서 vm name을 추출하는 로직 변경
예외 vm의 경우 vm name 뒤에 서버 ip 맨 뒤자리 추가 해야함 ex) name-203

2) ESXi memory 사용량에 따른 vm 강제 종료 추가
ESXi server의 memory 사용률이 90%가 넘으면 momory 사용량 top3 VM 중지

3) socket 통신 기능 추가
20000 port listen하여 manage web에서 on/off 명령을 받아 수행

4) log 설정 추가
vm 상태 업데이트 기록 및 app 동작 현황 파악을 위한 log 파일 생성 추가