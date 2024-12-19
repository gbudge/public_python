FROM python_soe:latest

ARG APP_SOURCE=default

WORKDIR /home/appuser/app

COPY apps/${APP_SOURCE}/requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt --upgrade pip

# CMD [ "sleep", "infinity" ]
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]