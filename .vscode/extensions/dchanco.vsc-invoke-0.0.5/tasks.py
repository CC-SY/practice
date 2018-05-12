from invoke import task

@task
def build(ctx, docs=False):
    ctx.run("echo Build!")

@task
def clean(ctx, docs=False):
   ctx.run("echo Clean!")