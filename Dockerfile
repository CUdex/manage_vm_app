FROM python:3.7.15-alpine3.17

MAINTAINER cuyu9779 <cuyu9779@gmail.com>
RUN apk add openssh sshpass
RUN pip install mysql-connector-python asyncio
RUN mkdir /usr/manage_vm
RUN sed -i 's/#   StrictHostKeyChecking ask/StrictHostKeyChecking no/g' /etc/ssh/ssh_config

COPY ./*.py /usr/manage_vm/

ENTRYPOINT ["/bin/sh","-c","if [ ! -f /root/.ssh/id_rsa ]; then ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa; fi && python3 /usr/manage_vm/manage_vm_app.py"]
