FROM ubuntu:focal

RUN apt-get update

ENV TZ 'PST8PDT'
RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

RUN apt-get install -y python3-pip libgdal-dev locales

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip3 install GDAL==3.0.4

ADD *.py .

CMD ["python3", "./org2org.py"]