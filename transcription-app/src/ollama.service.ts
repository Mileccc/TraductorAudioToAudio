import { Injectable, OnModuleInit, OnModuleDestroy, Inject, forwardRef  } from '@nestjs/common';
import * as http from 'http';
import { Ollama, HuggingFaceEmbedding, serviceContextFromDefaults } from 'llamaIndex';
import { AppGateway } from './app.gateway';

@Injectable()
export class OllamaService implements OnModuleInit, OnModuleDestroy {
    private baseURL: string = "http://127.0.0.1:11434";
    private model: string = "Traductor";
    private serviceContext: any;

    constructor(
        @Inject(forwardRef(() => AppGateway)) private appGateway: AppGateway,
    ) {
        this.initializeServiceContext();
    }

    async onModuleInit() {
        console.log("OllamaService iniciado");
    }

    async onModuleDestroy() {
        console.log("OllamaService destruido");
    }

    private initializeServiceContext() {
        const embedModel = new HuggingFaceEmbedding({
            modelType: 'Xenova/all-mpnet-base-v2', // Asegúrate de elegir el modelo correcto
        });

        // Inicializa Ollama con el contexto del servicio que incluye el modelo de embeddings
        this.serviceContext = serviceContextFromDefaults({
            llm: new Ollama({
                model: this.model,
                baseURL: this.baseURL
            }),
            embedModel: embedModel,
        });
    }

    async sendTranscription(transcription: string) {
        const translationPrompt = `Traduce el siguiente texto del español al inglés, manteniendo el significado original lo más fielmente posible:\n\n"${transcription}"`;

        const data = JSON.stringify({
            model: this.model,
            messages: [{ role: "user", content: translationPrompt }],
            options: {
                temperature: 0.3,
                top_p: 0.9,
            }
        });

        const options = {
            hostname: '127.0.0.1',
            port: 11434,
            path: '/api/chat',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data)
            }
        };

        const req = http.request(options, (res) => {
            let responseBody = '';
            
            // res.setEncoding('utf8');
            res.on('data', (chunk) => {
                responseBody += chunk;
            });

            res.on('end', () => {
                try {
                    //const responses = responseBody.split('\n').filter(line => line.trim());
                    const responses = this.processResponse(responseBody)
                    // responses.forEach(response => {
                    //     const responseJson = JSON.parse(response);
                    //     if (responseJson.message && responseJson.message.content) {
                    //         process.stdout.write(responseJson.message.content + ' ');

                    //         this.appGateway.server.emit('traduccion', responseJson.message.content);
                    //     }
                    // });
                    responses.forEach(response => {
                        this.appGateway.server.emit('traduccion', response)
                    })
                } catch (error) {
                    console.error("Error al procesar la respuesta completa:", error);
                }
            });
        });

        req.on('error', (error) => {
            console.error("Error al enviar transcripción a OLlama:", error);
        });

        req.write(data);
        req.end();
    }
    private processResponse(responseBody: string) {
        return responseBody.split('\n').filter(line => line.trim()).map(line => {
            const responseJson = JSON.parse(line)
            if (responseJson.message && responseJson.message.content) {
                process.stdout.write(responseJson.message.content)
                return responseJson.message.content
            }else {
                return null
            }
        }).filter(content => content !== null)
    }
}
