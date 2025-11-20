from src.llm.gemini_model import GeminiModel

gemini = GeminiModel(
    api_key='AIzaSyBYYHeJp7k4cCBcdbaJGTAnpvwmK_10O80',
    model="gemini-2.5-flash",
    proxy='http://192.168.31.112:10807'
)
print(gemini.test("hello gemini!"))