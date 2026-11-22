# enb-decision-api

Containerised Flask API that applies the Expected Net Benefit (ENB) pre-warm rule from my MSc thesis.

## What it does

- `POST /decide` takes `{"probability": 0.0-1.0}` and returns `PREWARM` or `SKIP`.
- Rule: `ENB = P x C_cold - C_warm`, with C_cold = $0.000808 and C_warm = $0.000083. Threshold is P > 10.3%.
- `GET /health` returns `{"status":"ok"}`.

## Architecture

Docker image -> Amazon ECR -> ECS Fargate task (public IP, security group restricted to the tester)

No ALB and no NAT gateway, to keep cost near zero.

## Run locally

    docker build -t enb-api:local .
    docker run -d --name enb-api -p 8080:8080 enb-api:local
    curl -X POST http://localhost:8080/decide -H "Content-Type: application/json" -d '{"probability":0.5}'

## Verification

| Probability | Result |
|---|---|
| 0.5 | PREWARM |
| 0.11 | PREWARM |
| 0.10 | SKIP |
| 0.05 | SKIP |
| 2 | HTTP 400 |

Same results locally and on ECS Fargate.

## Troubleshooting note

Requests to the Fargate task timed out with a correct-looking security group. My ISP rotates outbound IPs, so a single /32 rule never matched. I compared what two IP-check services saw, then allowed the ISP range for the test session and removed it afterwards.

## Cost

About $0.017/hour while a task runs. A test session cost 1 to 2 cents. ECR storage is under EUR 0.01/month.

## Teardown

    aws ecs stop-task --cluster enb-cluster --task <TASK_ARN> --region eu-west-1
    aws ecr delete-repository --repository-name enb-decision-api --region eu-west-1 --force

## Roadmap

- [ ] GitHub Actions build and push to ECR with OIDC
- [ ] Terraform for ECR, ECS and IAM
- [ ] ALB or API Gateway in front, replacing IP allow-lists
