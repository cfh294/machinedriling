FROM python:3.6
COPY . .
RUN pip install -r requirements.txt
RUN python -m spacy download en
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
