# Prepare the base environment.
FROM dbcawa/ledgergw:latest as builder_base_ledgergwdev

RUN apt-get update
RUN apt-get --no-install-recommends -y install nginx

RUN groupadd -g 1000 docker
RUN useradd -g 1000 -u 1000 docker -s /bin/bash
RUN mkdir /home/docker
RUN chown docker.docker /home/docker
RUN cp /root/.bashrc /home/docker
RUN cp /root/.profile /home/docker
RUN echo "cd /data/" >> /home/docker/.bashrc
RUN echo "export PS1='\e[0;31mdev:\e[m \e[0;32m${debian_chroot:+($debian_chroot)}\u@\h:\w\$\e[m '" >> /home/docker/.bashrc

EXPOSE 80
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:80/"]
CMD ["/startup.sh"]
