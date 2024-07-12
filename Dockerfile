FROM python_soe:latest

ARG APP_SOURCE=apps/default

COPY ${APP_SOURCE}/requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

WORKDIR /home/appuser/app

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]