import { AppGateway } from './app.gateway';
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { OllamaService } from './ollama.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService, AppGateway, OllamaService],
})
export class AppModule {}
