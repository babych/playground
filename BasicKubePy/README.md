# BasicKubePy

Deployed into K8S: [https://weather-api.172.199.209.31.nip.io/temperature?lat=50.45&lon=30.52](https://weather-api.172.199.209.31.nip.io/temperature?lat=50.45&lon=30.52)

App logs:

```bash
kubectl logs -l app=weather-api -n weather-api-ns --tail=100
```
