# Kubernetes HPA - Memory-Based Autoscaling

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

Proyek ini mengimplementasikan **Horizontal Pod Autoscaler (HPA)** di Kubernetes untuk melakukan *autoscaling* pod aplikasi Nginx secara dinamis berdasarkan metrik penggunaan memori (*memory utilization*).

---

## Specs & Configurations
* **Application**: Nginx Web Server
* **Replicas**: Min 2 | Max 5
* **Target Metric**: Memory Utilization at **75%**
* **Resources**:
  * `requests`: `100Mi` memory | `100m` cpu
  * `limits`: `200Mi` memory | `200m` cpu

---

## Repository Structure
```text
.
├── manifests/
│   ├── deployment.yaml   # Nginx Deployment + Resource Limits
│   ├── hpa.yaml          # HPA Configuration
│   └── service.yaml      # ClusterIP Service
└── README.md
```

## How to Run
1. Deploy Metrics Server (Prerequisite):
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
2. Apply Manifests:
```bash
kubectl apply -f manifests/
```
3. Check Status:
```bash
kubectl get deployment,hpa
```

## Key Highlights & Learnings
* **Apa itu HPA?:** Komponen Kubernetes yang menambah/mengurangi jumlah pod secara otomatis sesuai beban kerja agar performa stabil dan hemat resource.
* **Cara Kerja:** Metrics Server menghitung rata-rata pemakaian memori dari seluruh pod. Jika rata-rata melebihi 75% dari requests.memory, HPA akan trigger penambahan pod (max 5). Jika beban reda, HPA akan melakukan scale down secara bertahap (min 2).
* **Kenapa requests & limits Wajib?:** requests dipakai HPA sebagai baseline (100%) kalkulasi persentase metrik. limits mencegah pod mengonsumsi memori berlebih yang berpotensi memicu OOMKilled pada node.
* **Use Case:**Cocok untuk layanan yang memory-intensive saat trafik tinggi, seperti in-memory caching, pemrosesan dokumen/gambar, atau API gateway e-commerce.

## Load Testing
1. Pantau HPA real-time:
```bash
kubectl get hpa -w
```
2. JalankanPod Load Generator (Apache Bench):
```bash
kubectl run load-generator --image=httpd:alpine --restart=Never -- ab -n 500000 -c 600 http://nginx-service/
```
3. **Hasil:**
* Peningkatan trafik HTTP secara simultan memicu kenaikan metrik resource pada pod Nginx.
* Nilai metrik pada kolom TARGETS akan naik
* HPA secara otomatis melakukan scale-up jumlah pod dari 2 hingga 5 pod untuk menjaga ketersediaan layanan.
4. Hentikan Load Generator (Scale-Down):
```bash
kubectl delete pod load-generator
```
