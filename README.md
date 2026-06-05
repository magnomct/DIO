# 🏗️ Projetos de Arquitetura AWS: Tradicional vs. Serverless

> Documentação técnica de infraestruturas projetadas na AWS, demonstrando dois paradigmas distintos: uma arquitetura tradicional baseada em instâncias (IaaS) com foco em alta disponibilidade e uma arquitetura orientada a eventos (Serverless) focada em escalabilidade nativa e baixo custo operacional.

---

## 📋 Índice

- [1. Arquitetura Tradicional — EC2 + EBS com Alta Disponibilidade](#1-arquitetura-tradicional--ec2--ebs-com-alta-disponibilidade)
  - [Visão Geral (EC2/EBS)](#visão-geral-ec2ebs)
  - [Componentes da Infraestrutura (EC2/EBS)](#componentes-da-infraestrutura-ec2ebs)
  - [Fluxo de Tráfego (EC2/EBS)](#fluxo-de-tráfego-ec2ebs)
- [2. Arquitetura Serverless — S3 + API Gateway + Lambda + DynamoDB](#2-arquitetura-serverless--s3--api-gateway--lambda--dynamodb)
  - [Visão Geral (Serverless)](#visão-geral-serverless)
  - [Componentes da Infraestrutura (Serverless)](#componentes-da-infraestrutura-serverless)
  - [Fluxo de Tráfego (Serverless)](#fluxo-de-tráfego-serverless)
- [⚖️ Comparativo Arquitetural](#️-comparativo-arquitetural)
- [Segurança e Resiliência (Geral)](#segurança-e-resiliência-geral)
- [📎 Referências](#-referências)

---

## 1. Arquitetura Tradicional — EC2 + EBS com Alta Disponibilidade

Esta arquitetura implementa uma aplicação web distribuída em **duas Zonas de Disponibilidade (AZs)** dentro de uma única **Região AWS**. O design segue as boas práticas do AWS Well-Architected Framework, garantindo separação clara entre camadas públicas e privadas.

### Visão Geral (EC2/EBS)

| Atributo | Detalhe |
|---|---|
| **Regiões e AZs** | 1 Região AWS (AZ-01 e AZ-02) |
| **Rede (VPC CIDR)** | `10.0.0.0/24` |
| **Modelo de Acesso** | Público via Route 53 + ALB; Privado via NAT Gateway |
| **Processamento** | EC2 via Auto Scaling Group |
| **Banco de Dados** | RDS em subnet privada por AZ |

### Componentes da Infraestrutura (EC2/EBS)

* **DNS (Route 53):** Realiza resolução de nomes de domínio e roteia usuários para o Application Load Balancer.
* **VPC e Internet Gateway:** Rede isolada (`10.0.0.0/24`) conectada à internet pública para tráfego bidirecional.
* **Subnets Públicas e NAT Gateways:** Hospedam os NAT Gateways para permitir acesso de saída seguro das instâncias em subnets privadas.
* **Application Load Balancer (ALB):** Distribui tráfego (HTTP/HTTPS) entre instâncias nas duas AZs e realiza health checks.
* **Auto Scaling Group (ASG):** Escala as instâncias EC2 horizontalmente conforme a demanda e substitui servidores com falha.
* **Subnets Privadas e EC2:** Hospedam os servidores de aplicação (EC2) sem acesso direto à internet.
* **Armazenamento (EBS):** Volumes de bloco persistentes e atrelados individualmente a cada instância EC2.
* **Banco de Dados (RDS):** Serviço relacional em subnet privada, preparado para Multi-AZ Deployment (failover automático).

### Fluxo de Tráfego (EC2/EBS)

**Entrada (Ingress):**
1. Usuário acessa o domínio resolvido pelo Route 53.
2. O tráfego chega ao Application Load Balancer.
3. O ALB distribui a requisição para uma Instância EC2 na Subnet Privada (AZ-01 ou AZ-02).
4. A instância processa dados lendo do EBS e interagindo com o RDS.

**Saída (Egress):**
1. A Instância EC2 solicita pacotes/atualizações.
2. O tráfego é direcionado ao NAT Gateway na Subnet Pública da respectiva AZ.
3. O pacote sai para a internet pelo Internet Gateway.

---

## 2. Arquitetura Serverless — S3 + API Gateway + Lambda + DynamoDB

Esta arquitetura elimina o gerenciamento de servidores, implementando um frontend estático isolado e um backend orientado a eventos. Focada em reduzir o custo operacional e oferecer escala sob demanda.

### Visão Geral (Serverless)

| Atributo | Detalhe |
|---|---|
| **Modelo de Computação** | Serverless (sem servidores para gerenciar) |
| **Frontend** | Aplicação React hospedada no Amazon S3 |
| **Orquestração de API** | AWS API Gateway (REST/HTTP API) |
| **Backend** | Funções AWS Lambda (Node.JS, .NET Core, Python) |
| **Banco de Dados** | Amazon DynamoDB (NoSQL on-demand) |

### Componentes da Infraestrutura (Serverless)

* **Amazon S3 (Frontend):** Atua como servidor de arquivos estáticos (HTML, CSS, JS) com Static Website Hosting.
* **Triggers do S3:** Eventos automáticos que acionam Lambdas após uploads de arquivos.
* **AWS API Gateway:** Roteador proxy que expõe endpoints REST, gerencia autenticação, throttling e CORS.
* **AWS Lambda:** Núcleo de processamento stateless, executado sob demanda e com escala de zero a milhares de execuções concorrentes.
* **Amazon DynamoDB:** Banco de dados NoSQL gerenciado com latência de milissegundos e escala automática, utilizando modelagem baseada em partições.

### Fluxo de Tráfego (Serverless)

**Carregamento Front-End:**
1. O Browser do usuário faz um `GET` no Amazon S3.
2. O S3 retorna os assets estáticos (React bundle).

**Chamadas de API (Dinâmicas):**
1. A aplicação React envia uma requisição HTTP ao API Gateway.
2. O API Gateway roteia o payload para a função Lambda correspondente via Trigger.
3. A função Lambda processa a lógica de negócio e lê/escreve dados no DynamoDB.

**Processamento Assíncrono:**
1. Usuário faz upload de um arquivo para o S3.
2. O S3 gera um evento automático que aciona uma Lambda para processamento em background.

---

## ⚖️ Comparativo Arquitetural

| Aspecto | EC2 + EBS (Tradicional / IaaS) | S3 + Lambda + DynamoDB (Serverless) |
|---|---|---|
| **Gerenciamento** | Alto (patches, SO, scaling manual) | Zero (totalmente gerenciado pela AWS) |
| **Custo em Idle** | Alto (instâncias cobradas 24/7) | Zero (cobrança apenas por uso real) |
| **Escalabilidade** | Minutos (via Auto Scaling Group) | Segundos (escala automática nativa) |
| **Disponibilidade** | Requer configuração Multi-AZ explícita | Nativa em todos os serviços |
| **Estado (State)** | Persistido localmente no EBS (Stateful) | Externalizado no DynamoDB (Stateless) |
| **Casos de Uso Ideais** | Sistemas legados, bancos relacionais (SQL), processamento contínuo | APIs modernas, microsserviços, arquitetura orientada a eventos, SPAs |
| **Cold Start** | Não aplicável | Pode ocorrer latência inicial nas Lambdas |

---

## Segurança e Resiliência (Geral)

Independentemente do paradigma escolhido, ambas as arquiteturas compartilham princípios robustos de segurança e resiliência:

* **Princípio do Menor Privilégio:** Utilização rigorosa de IAM Roles e Security Groups.
* **Criptografia:** Dados protegidos em repouso (AWS KMS em EBS, RDS, S3, DynamoDB) e em trânsito (TLS/SSL).
* **Auditoria e Proteção:** Recomenda-se o uso de AWS WAF contra ataques na camada web, AWS CloudTrail para logs de auditoria de chamadas de API, e AWS Secrets Manager para evitar credenciais estáticas no código.

---

## 📎 Referências

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)
- [Amazon EC2 e EBS Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
