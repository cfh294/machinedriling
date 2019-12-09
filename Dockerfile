FROM tensorflow/tensorflow:1.13.1-gpu-py3

RUN apt-get update && apt-get install -y --no-install-recommends wget

RUN pip3 install regex ai-integration==1.0.11
RUN pip3 install tensorflow-gpu

WORKDIR /model

# RUN mkdir PrettyBig
# RUN wget -nc https://deepai-opensource-codebases-models.s3-us-west-2.amazonaws.com/gpt2-prettybig/PrettyBig/checkpoint -O PrettyBig/checkpoint
# RUN wget -nc https://deepai-opensource-codebases-models.s3-us-west-2.amazonaws.com/gpt2-prettybig/PrettyBig/model.ckpt.index -O PrettyBig/model.ckpt.index
# RUN wget -nc https://deepai-opensource-codebases-models.s3-us-west-2.amazonaws.com/gpt2-prettybig/PrettyBig/model.ckpt.meta -O PrettyBig/model.ckpt.meta
# RUN wget -nc https://deepai-opensource-codebases-models.s3-us-west-2.amazonaws.com/gpt2-prettybig/PrettyBig/model.ckpt.data-00000-of-00001 -O PrettyBig/model.ckpt.data-00000-of-00001

COPY . /model


CMD []
ENTRYPOINT ["python3", "main.py"]