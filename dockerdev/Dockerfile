# Prepare the base environment.
FROM dbcawa/ledgergw:latest as builder_base_ledgergwdev
USER root

RUN apt-get update
# RUN apt-get --no-install-recommends -y install nginx
# RUN apt-get install --no-install-recommends -y virtualenv
# RUN apt-get install -y graphviz
# RUN apt-get install -y python3-pydot

RUN echo 'if ! [ -n "${SUDO_USER}" -a -n "${SUDO_PS1}" ]; then' >> /etc/bash.bashrc
#RUN echo "export PS1='\[\e[0;31mdev:\e[0;32m \u@\h:~ \e[0;34m\W\$\e\[\e[0m\] '" >> /etc/bash.bashrc
# fix the line carriage issue
RUN echo "export PS1='\[\e[;31m\]dev:\[\e[m\] \[\e[;32m\]\u@\h:\w \$ \[\e[m\]'" >> /etc/bash.bashrc
RUN echo "fi" >> /etc/bash.bashrc

# For windows
#RUN groupadd -g 1000 docker
#RUN useradd -g 1000 -u 1000 docker -s /bin/bash
#RUN mkdir /home/docker

# For Linux
RUN groupadd -g 20000 container
RUN useradd -g 20000 -u 200000 container -s /bin/bash
RUN mkdir /home/container
RUN chown container.container /home/container

# RUN cp /root/.bashrc /home/docker
RUN cp /root/.profile /home/docker

EXPOSE 80
USER oim
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:80/"]
CMD ["/startup.sh"]
