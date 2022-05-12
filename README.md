# hanghaeMusic99 🎧
## Chapter1 웹개발 미니 프로젝트 (항해뮤직99)

### music platform에서 가져온 실시간 Top 99위 까지의 노래에 자유롭게 코멘트를 작성하며 소통할 수 있는 웹입니다.

## 1. 제작기간 & 팀원소개
- 2022년 5월 9일 ~ 2022년 5월 12일
- 4인 1조 팀 프로젝트
  - 최지훈
  - 문희린
  - 송완준
  - 김형준

## 2. 사용 기술
`Back-end`
- Python 3
- Flask 2.1.1
- MongoDB

`Front-end`
- JQuery 3.5.1
- Bulma 0.9.2
- Bootstrap 5.0.2

`deploy`
- AWS EC2(Ubuntu 18.04 LTS)

### 3. 실행화면
[![항해뮤직99!](https://i.ytimg.com/vi/BWq5Yj9aafs/hqdefault.jpg)](https://youtu.be/BWq5Yj9aafs)

### 4. 핵심기능
- 실시간 크롤링
  - apscheduler 라이브러리를 import하여 6시간 마다 멜론 실시간 top 99위 까지의 음원을 크롤링 합니다.

- 로그인, 회원가입
  - 정규식을 통해 ID, PW validation을 체크했습니다.
  - JWT를 사용하여 로그인 기능을 구현했습니다. (로그인 시 JWT 토큰 발급, 클라이언트 사이드에 저장)

- 리뷰 CRUD
  - 음원의 상세페이지에는 해당 음원에 작성된 리뷰들이 조회됩니다. ->Read
  - 음원의 상세페이지에서 본인의 계정 정보를 담은 리뷰를 작성할 수 있습니다. -> Create
  - 발급된 토큰을 기준으로 본인의 리뷰에만 수정, 삭제 버튼이 표출됩니다. -> Update, Delete
 
- 마이페이지 구현
  - 본인이 좋아요 누른 음원들을 listup
  - 프로필 정보를 수정할 수 있습니다. (이름, 사진, 한마디)

### 5. 링크
- SA: https://velog.io/@rlafbf222/%ED%95%AD%ED%95%B4-Chapter1-%EC%9B%B9%EA%B0%9C%EB%B0%9C-%EB%AF%B8%EB%8B%88-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-7%EA%B8%B0-d%EB%B0%98-8%EC%A1%B0
