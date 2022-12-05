FROM python:3.7.15-alpine3.17

MAINTAINER cuyu9779 <cuyu9779@gmail.com>
RUN apk add openssh
RUN pip install mysql-connector-python
RUN mkdir /usr/manage_vm
RUN sed -i 's/#   StrictHostKeyChecking ask/StrictHostKeyChecking no/g' /etc/ssh/ssh_config

COPY ./manage_vm_app.py /usr/manage_vm/
COPY ./mysql_lib.py /usr/manage_vm/
COPY ./vm_utils.py /usr/manage_vm/

CMD ["/bin/sh","-c","if [ ! -f /root/.ssh/id_rsa ]; then ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa; fi && python3 /usr/manage_vm/manage_vm_app.py"]
