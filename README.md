# 마부장 DB 상태 확인

고객 자료를 읽거나 쓰지 않고, 고정 상태만 반환하는 DB 함수를 하루 네 번 조회한다. Python 표준 라이브러리만 사용한다.

## 공개되는 정보

이 저장소의 파일 3개, 실행 시각·성공/실패·HTTP 상태/오류 종류, 장애·복구 이슈가 공개된다. 앱 소스·설치 파일·고객 콘텐츠는 포함하지 않는다. DB 주소와 공개 publishable key도 파일에 넣지 않고 저장소 Actions secrets로 설정한다. 서비스 키·DB 비밀번호·관리 토큰은 사용하지 않는다.

## 설정

1. 이 폴더의 파일 3개만 별도 **공개** 저장소의 기본 브랜치에 올린다. 기존 앱 저장소는 비공개로 유지한다.
2. Settings → Secrets and variables → Actions → Repository secrets에 `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`를 등록한다. 후자는 기존 앱에서 쓰는 공개 키이며 특권 키를 넣으면 안 된다.
3. Actions → Supabase DB heartbeat → Run workflow에서 두 시험 옵션을 끈 채 한 번 실행하고 `Database RPC returned ok=true`를 확인한다.
4. 실제 정기 실행까지 성공한 다음 기존 비공개 저장소의 heartbeat만 Disable한다. 다른 빌드 워크플로와 다운로드·업데이트는 그대로 둔다.

## 실행·알림

- UTC 01:17·07:17·13:17·19:17, 한국 10:17·16:17·22:17·다음 날 04:17. 예약 실행은 지연될 수 있다.
- DB RPC `vendor_healthcheck()`의 `{"ok":true}`만 확인한다. 최대 3회, 요청당 20초, 재시도 간격 10초다.
- 장애가 시작되면 이 저장소에 이슈를 만들고 저장소 소유자 `god12070521-prog`에게 배정한다. 중복을 억제하고, 다음 성공 때 복구 댓글과 함께 닫는다. 이메일 수신은 소유자의 GitHub 알림 설정에 따른다.
- 알림 시험은 두 시험 옵션을 켜고 실행한 뒤 `notification_test`만 켜고 다시 실행한다. 실제 장애 알림과 시험 이슈는 분리된다.

## 비용·제한

표준 Ubuntu 실행기만 사용한다. artifact·cache·Packages 업로드가 없고, 공개 저장소일 때만 실행하도록 제한했다. 공개 저장소의 표준 실행기는 무료다. 결제수단·유료 예산 변경은 필요 없다.

공개 저장소에 60일간 활동이 없으면 GitHub가 정기 실행을 자동 중지할 수 있으므로 저장소를 관리하며 중지 여부를 확인해야 한다. 정기 조회가 Supabase 자동 중지 방지를 보장하지 않으며, 멈춘 DB를 자동 재개하거나 유료 플랜으로 바꾸지 않는다. 비공개 앱 저장소의 Windows 빌드 무료 한도 문제는 별도다.

근거: [GitHub Actions 비용](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [예약 실행 조건](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
