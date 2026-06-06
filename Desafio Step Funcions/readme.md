# 📑 Orquestração de Backup Automatizado de EBS com AWS Step Functions

> Este repositório contém a definição e documentação de um workflow automatizado utilizando **AWS Step Functions (Amazon States Language - ASL)** para gerenciar o ciclo de vida de backups de volumes Amazon EBS, integrado à arquitetura tradicional de alta disponibilidade (EC2/EBS).

O objetivo deste projeto é eliminar intervenções manuais ou a necessidade de gerenciar scripts de agendamento internos em instâncias EC2, substituindo-os por uma orquestração serverless nativa, resiliente e imutável que utiliza o **AWS SDK Integration** direto do Step Functions.

---

## 📋 Índice

- [1. Visão Geral do Workflow](#1-visão-geral-do-workflow)
- [2. Diagrama Lógico de Estados](#2-diagrama-lógico-de-estados)
- [3. Definição da State Machine (ASL)](#3-definição-da-state-machine-asl)
- [4. Detalhamento dos Estados](#4-detalhamento-dos-estados)
- [5. Pré-requisitos e Permissões IAM](#5-pré-requisitos-e-permissões-iam)
- [6. Como Executar](#6-como-executar)
- [7. Monitoramento e Tratamento de Erros](#7-monitoramento-e-tratamento-de-erros)

---

## 1. Visão Geral do Workflow

Na arquitetura de infraestrutura tradicional com EC2, a persistência de dados ocorre nos volumes **Amazon EBS**. Para garantir uma estratégia robusta de _Disaster Recovery (DR)_, é fundamental realizar snapshots periódicos desses volumes.

Este workflow automatiza o seguinte processo:

1. Inicia a criação de um snapshot de um volume específico fornecido na entrada.
2. Aguarda um intervalo de tempo predefinido (60 segundos) para mitigar o impacto de volumes densos.
3. Consulta o status do snapshot iterativamente até que ele seja concluído ou falhe.
4. Notifica a equipe de operações via **Amazon SNS** com o status final da operação (Sucesso ou Falha).

---

## 2. Diagrama Lógico de Estados

O comportamento do fluxo segue a máquina de estados abaixo:

````text
       [ Início ]
           │
           ▼
    [ CreateSnapshot ]
           │
           ▼
 ┌──► [ WaitForSnapshot ] (Espera de 60s)
 │         │
 │         ▼
 │  [ CheckSnapshotStatus ]
 │         │
 │         ▼
 └─── [ IsSnapshotCompleted? ] ──( erro )──► [ NotifyFailure ] ──► [ Fim ]
           │
      ( completed )
           │
           ▼
    [ NotifySuccess ]
           │
           ▼
        [ Fim ]

## 3. Definição-da-state-machine-asl (code.json)

## 4. Diagrama Lógico de Estados

Detalhamento dos Estados

A. CreateSnapshot
Usa a integração otimizada com o AWS SDK para chamar a API ec2:createSnapshot. Ele mapeia dinamicamente o parâmetro de entrada VolumeId enviado na execução. O resultado contendo o SnapshotId gerado é injetado no nó $.SnapshotResult.

B. WaitForSnapshot
Um estado do tipo Wait que pausa o workflow por 60 segundos. Isso evita requisições excessivas (throttling) na API da AWS enquanto o processo de cópia de blocos ocorre em background na infraestrutura global da AWS.

C. CheckSnapshotStatus
Chama a API ec2:describeSnapshots filtrando especificamente pelo SnapshotId criado no primeiro passo.

D. IsSnapshotCompleted
Um estado do tipo Choice (Decisão). Ele analisa o array retornado pela consulta e verifica o campo de estado (State):

Se for igual a "completed", o fluxo avança para a notificação de êxito.

Se for igual a "error", avança para a notificação de falha.

Se estiver em qualquer outro estado intermediário (como "pending"), o loop é acionado, retornando para o WaitForSnapshot.

E. NotifySuccess / NotifyFailure
Utilizam o serviço Amazon SNS (Simple Notification Service) para enviar mensagens para um tópico configurado (subscrito por e-mail, SMS, Chatbot ou PagerDuty), alertando o time de DevOps sobre o encerramento do processo.

5. Pré-requisitos e Permissões IAM
Para que a State Machine seja executada corretamente, a IAM Role associada ao Step Functions precisa de uma política integrada que dê permissões explícitas sobre o EC2 e SNS.

Exemplo de Política IAM (Menor Privilégio):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateSnapshot",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:SUA-REGIAO:SUA-CONTA:EBS-Backup-Alerts"
    }
  ]
}
````

6. Como Executar
   Ao iniciar uma nova execução da State Machine, insira o seguinte payload JSON como entrada, substituindo pelo ID real do volume EBS anexado à sua instância EC2:

{
"VolumeId": "vol-0a1b2c3d4e5f6g7h8"
}

---

7. Monitoramento e Tratamento de Erros
   O AWS Step Functions grava logs detalhados de cada transição de estado. Em cenários de produção, recomenda-se habilitar a integração com o Amazon CloudWatch Logs na aba de configurações da State Machine para rastreamento de auditoria e conformidade técnica.
