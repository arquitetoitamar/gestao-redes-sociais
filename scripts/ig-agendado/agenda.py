#!/usr/bin/env python3
"""Agenda posts do @tiopstecnologia na AWS (EventBridge Scheduler -> Lambda tiops-ig-agendado).
Não depende do Mac ligado na hora de publicar.

  python3 agenda.py infra                      cria/atualiza segredo, papéis e a Lambda
  python3 agenda.py agenda <id> reel|imagem <arquivo> <legenda.md> "AAAA-MM-DD HH:MM" [capa_ms]
  python3 agenda.py lista                      agendamentos pendentes e resultados
  python3 agenda.py cancela <id>

A legenda é o texto de legenda.md entre o título (# ...) e a linha "---"; o bloco
"Primeiro comentário" depois do "---" vira o comentário publicado logo após o post.
O token sai de ~/.hermes/credentials/instagram_config.json direto para o Secrets Manager (nunca é impresso).
"""
import io, json, os, sys, time, zipfile
import boto3

REG = 'us-east-1'
BUCKET = 'tiops-public-assets-1785392019'
SECRET = 'tiops/instagram/tiopstecnologia'
FN = 'tiops-ig-agendado'
ROLE_FN = 'tiops-ig-agendado-lambda'
ROLE_SCH = 'tiops-ig-agendado-scheduler'
AQUI = os.path.dirname(os.path.abspath(__file__))
s = boto3.session.Session(region_name=REG)
iam, lam, sm, s3, sch, sts = (s.client(x) for x in ('iam', 'lambda', 'secretsmanager', 's3', 'scheduler', 'sts'))
CONTA = sts.get_caller_identity()['Account']


def papel(nome, servico, politica):
    confia = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Principal': {'Service': servico}, 'Action': 'sts:AssumeRole'}]}
    try:
        arn = iam.get_role(RoleName=nome)['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        arn = iam.create_role(RoleName=nome, AssumeRolePolicyDocument=json.dumps(confia),
                              Description='Posts agendados do Instagram @tiopstecnologia')['Role']['Arn']
        time.sleep(12)
    iam.put_role_policy(RoleName=nome, PolicyName='acesso', PolicyDocument=json.dumps(politica))
    return arn


def infra():
    cfg = json.load(open(os.path.expanduser('~/.hermes/credentials/instagram_config.json')))
    segredo = json.dumps({'ig_account_id': cfg['ig_account_id'], 'token': cfg.get('page_access_token') or cfg['access_token']})
    try:
        sec_arn = sm.create_secret(Name=SECRET, SecretString=segredo, Description='Token de página do @tiopstecnologia (posts agendados)')['ARN']
    except sm.exceptions.ResourceExistsException:
        sec_arn = sm.put_secret_value(SecretId=SECRET, SecretString=segredo)['ARN']
    fn_arn = 'arn:aws:lambda:%s:%s:function:%s' % (REG, CONTA, FN)
    r_fn = papel(ROLE_FN, 'lambda.amazonaws.com', {'Version': '2012-10-17', 'Statement': [
        {'Effect': 'Allow', 'Action': ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'], 'Resource': '*'},
        {'Effect': 'Allow', 'Action': 'secretsmanager:GetSecretValue', 'Resource': sec_arn},
        {'Effect': 'Allow', 'Action': ['s3:GetObject', 's3:PutObject', 's3:DeleteObject'],
         'Resource': ['arn:aws:s3:::%s/agendados-estado/*' % BUCKET, 'arn:aws:s3:::%s/temp/agendados/*' % BUCKET]}]})
    papel(ROLE_SCH, 'scheduler.amazonaws.com', {'Version': '2012-10-17', 'Statement': [
        {'Effect': 'Allow', 'Action': 'lambda:InvokeFunction', 'Resource': [fn_arn, fn_arn + ':*']}]})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(AQUI, 'lambda_function.py'), 'lambda_function.py')
    env = {'Variables': {'BUCKET': BUCKET, 'SECRET': SECRET}}
    try:
        lam.get_function(FunctionName=FN)
        lam.update_function_code(FunctionName=FN, ZipFile=buf.getvalue())
        lam.get_waiter('function_updated_v2').wait(FunctionName=FN)
        lam.update_function_configuration(FunctionName=FN, Environment=env, Timeout=900, MemorySize=256)
    except lam.exceptions.ResourceNotFoundException:
        for tentativa in range(5):
            try:
                lam.create_function(FunctionName=FN, Runtime='python3.12', Role=r_fn, Handler='lambda_function.handler',
                                    Code={'ZipFile': buf.getvalue()}, Timeout=900, MemorySize=256, Environment=env,
                                    Description='Publica posts agendados no Instagram @tiopstecnologia')
                break
            except lam.exceptions.InvalidParameterValueException:
                time.sleep(8)        # papel recém-criado ainda propagando
    lam.get_waiter('function_active_v2').wait(FunctionName=FN)
    lam.get_waiter('function_updated_v2').wait(FunctionName=FN)
    # nunca repetir: uma segunda tentativa poderia postar duas vezes
    lam.put_function_event_invoke_config(FunctionName=FN, MaximumRetryAttempts=0, MaximumEventAgeInSeconds=3600)
    print('infra ok:', FN)


def textos(md):
    corpo, _, resto = open(md).read().partition('\n---\n')
    legenda = '\n'.join(l for l in corpo.splitlines() if not l.startswith('# ')).strip()
    com = []
    for bloco in resto.strip().split('\n\n'):
        linhas = bloco.splitlines()
        if linhas and linhas[0].lower().startswith('primeiro comentário'):
            com = linhas[1:]
    return legenda, '\n'.join(com).strip()


def agenda(pid, tipo, arquivo, md, quando, capa=None):
    legenda, comentario = textos(md)
    assert len(legenda) <= 2200 and legenda.count('#') <= 30
    key = 'temp/agendados/%s%s' % (pid, os.path.splitext(arquivo)[1])
    s3.upload_file(arquivo, BUCKET, key, ExtraArgs={'ContentType': 'video/mp4' if tipo == 'reel' else 'image/jpeg'})
    url = 'https://%s.s3.amazonaws.com/%s' % (BUCKET, key)
    ev = {'id': pid, 'tipo': tipo, 'url': url, 'key': key, 'caption': legenda, 'comentario': comentario, 'apagar_midia': True}
    if capa is not None:
        ev['thumb_offset'] = int(capa)
    teste = json.loads(lam.invoke(FunctionName=FN, Payload=json.dumps(dict(ev, teste=True)).encode())['Payload'].read())
    print('teste:', teste)
    assert teste.get('midia_http') == 200 and teste.get('conta') == 'tiopstecnologia' and not teste.get('ja_rodou'), teste
    data, hora = quando.split()
    nome = 'ig-' + pid
    alvo = {'Arn': 'arn:aws:lambda:%s:%s:function:%s' % (REG, CONTA, FN),
            'RoleArn': 'arn:aws:iam::%s:role/%s' % (CONTA, ROLE_SCH),
            'Input': json.dumps(ev, ensure_ascii=False), 'RetryPolicy': {'MaximumRetryAttempts': 0}}
    try:
        sch.delete_schedule(Name=nome)
    except sch.exceptions.ResourceNotFoundException:
        pass
    sch.create_schedule(Name=nome, ScheduleExpression='at(%sT%s:00)' % (data, hora), ScheduleExpressionTimezone='America/Sao_Paulo',
                        FlexibleTimeWindow={'Mode': 'OFF'}, Target=alvo, ActionAfterCompletion='DELETE',
                        Description='Post agendado %s (%s)' % (pid, tipo))
    print('agendado:', nome, quando, 'BRT')


def lista():
    for x in sch.list_schedules(NamePrefix='ig-')['Schedules']:
        d = sch.get_schedule(Name=x['Name'])
        print('pendente:', x['Name'], d['ScheduleExpression'], d['ScheduleExpressionTimezone'])
    for o in s3.list_objects_v2(Bucket=BUCKET, Prefix='agendados-estado/').get('Contents', []):
        print('resultado:', o['Key'], s3.get_object(Bucket=BUCKET, Key=o['Key'])['Body'].read().decode()[:300])


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'infra':
        infra()
    elif cmd == 'agenda':
        agenda(*sys.argv[2:])
    elif cmd == 'lista':
        lista()
    elif cmd == 'cancela':
        sch.delete_schedule(Name='ig-' + sys.argv[2]); print('cancelado')
