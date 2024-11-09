from twisted.internet import reactor, endpoints
from twisted.web import server, resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet.threads import deferToThread
import json
import torch
from transformers import pipeline
import sys

# Initialize the LLaMA model
model_id = "meta-llama/Llama-3.2-1B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

system_requarenments = str()

def process_with_llama(user_input):
    """
    Process input text through LLaMA model
    """
    messages = [
        {"role": "system", "content": system_requarenments},
        {"role": "user", "content": user_input},
    ]
    
    outputs = pipe(
        messages,
        max_new_tokens=264,
        top_k=50,
        top_p=0.7,
        temperature=0.7,
    )
    
    return outputs[0]["generated_text"][-1]

# HTTP Request Handler
class HTTPMessageServer(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        def handle_response(llama_response):
            response = {
                "status": "success",
                "original_message": message,
                "llama_response": llama_response,
                "timestamp": reactor.seconds()
            }
            request.setHeader('Content-Type', 'application/json')
            request.write(json.dumps(response).encode('utf-8'))
            request.finish()

        def handle_error(error):
            request.setResponseCode(400)
            error_response = {
                "status": "error",
                "message": str(error)
            }
            request.setHeader('Content-Type', 'application/json')
            request.write(json.dumps(error_response).encode('utf-8'))
            request.finish()

        try:
            # Read the content from the request
            content = request.content.read()
            message = content.decode('utf-8')
            print(f"Received HTTP POST: {message}")

            # Process the message through LLaMA in a separate thread
            d = deferToThread(process_with_llama, message)
            d.addCallback(handle_response)
            d.addErrback(handle_error)

            return NOT_DONE_YET

        except Exception as e:
            request.setResponseCode(400)
            error_response = {
                "status": "error",
                "message": str(e)
            }
            request.setHeader('Content-Type', 'application/json')
            return json.dumps(error_response).encode('utf-8')

    def render_GET(self, request):
        response = {
            "status": "success",
            "message": "LLaMA-integrated server is running",
            "timestamp": reactor.seconds()
        }
        request.setHeader('Content-Type', 'application/json')
        return json.dumps(response).encode('utf-8')

def main():
    if len(sys.argv) > 1:
        global system_requarenments
        system_requarenments = sys.argv[1]
        
    print(f"System requirements: {system_requarenments}")
    
    # Set up HTTP server
    http_endpoint = endpoints.TCP4ServerEndpoint(reactor, 8008)
    http_endpoint.listen(server.Site(HTTPMessageServer()))
    print("HTTP Server started on port 8008")

    # Start the reactor
    reactor.run()

if __name__ == "__main__":
    if torch.cuda.is_available():
        print("CUDA is available. Using GPU.")
    else:
        print("CUDA is not available. Using CPU.")
    main()