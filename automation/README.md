# Облачный технический видеоконвейер

Пилот собирает только утверждённый технический fixture из `automation/pilot/approved/`. Он проверяет техническую сборку MP4, но не является готовым рекламным роликом.

## Запуск

Откройте GitHub Actions → **Video pipeline pilot** → **Run workflow**. Сборка сохраняет artifact `pilot-mp4-and-qa`. Загрузка на Google Drive запускается только если заданы все три repository variables ниже; имена файлов содержат ID запуска, чтобы тесты не перезаписывали друг друга.

## Безопасное подключение Google Drive

Workflow использует GitHub OIDC и краткоживущий access token. JSON-ключ сервисного аккаунта и секрет `GDRIVE_SA_JSON` больше не нужны. В настройках репозитория добавьте Variables:

- `GCP_WIF_PROVIDER` — полный resource name OIDC provider, например `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER`.
- `GCP_SERVICE_ACCOUNT` — email выделенного service account.
- `GDRIVE_FOLDER_ID` — ID целевой папки Google Drive.

В Google Cloud настройте Workload Identity Federation для issuer `https://token.actions.githubusercontent.com/`. Ограничьте provider условиями для репозитория `Yachtsexpert/rangemarine-video-1`, ветки `refs/heads/main` и workflow `.github/workflows/video-pipeline-pilot.yml`. На service account выдайте `roles/iam.workloadIdentityUser` только федеративному principal этого репозитория. Не создавайте и не загружайте JSON-ключ.

Включите Google Drive API и предоставьте этому service account доступ редактора только к целевой папке. Workflow запрашивает OAuth scope `https://www.googleapis.com/auth/drive.file`, загружает MP4 и `qa.json`, затем перечитывает metadata созданных файлов и сверяет папку, имя и размер.

Проверки: длительность, разрешение, H.264, SHA-256 и сверка Drive metadata. Звук, лицензии, достоверность содержимого, водяные знаки и полный 9-этапный производственный контроль этот fixture не проверяет.