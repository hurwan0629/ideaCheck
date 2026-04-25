from ai_client import client

def analyze_company(company_name: str, info: dict):
  response = client.responses.create(
    model="gpt-4o",
    input=f"""
  다음은 {company_name}의 위키피디아 문서에서 추출한 정보야.
  이 기업에 대한 강점, 약점, 특징을 정리해라.
  ---
  아래 규칙을 반드시 지켜라.
  1. 반드시 한국어로만 작성한다.
  2. 출력은 JSON 객체만 반환한다.
  3. ``` 같은 마크다운 코드블록을 절대 사용하지 않는다.
  4. json, 설명문, 인사말, 부가 텍스트를 붙이지 않는다.
  5. 바로 {{ 로 시작해서 }} 로 끝나는 순수 JSON만 출력한다.
  ---
  {info}
  """
  )

  # print(response)

  return response.output_text