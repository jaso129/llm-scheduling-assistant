package com.example.notiontest.Service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

@Service
public class NotionService {
    private final String token;
    private final String databaseId;

    public NotionService(
            @Value("${notion.api.token}") String token,
            @Value("${notion.database.id}") String databaseId
    ) {
        this.token = token;
        this.databaseId = databaseId;
    }

    public void createNotionPage(String title, String notes, String dateIsoString){
        // 1. 組JSON
        String json = """
        {
          "parent": { "database_id": "%s" },
          "properties": {
            "Name": {
              "title": [
                {
                  "text": { "content": "%s" }
                }
              ]
            },
            "Notes": {
              "rich_text": [
                {
                  "text": { "content": "%s" }
                }
              ]
            },
            "Date": {
              "date": {
                "start": "%s"
              }
            }
          }
        }
        """.formatted(databaseId, title, notes, dateIsoString);

        // 2. 建立Request
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.notion.com/v1/pages"))
                .header("Authorization", "Bearer " + token)
                .header("Content-Type", "application/json")
                .header("Notion-Version", "2022-06-28")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        // 3. 建立Client
        HttpClient client = HttpClient.newHttpClient();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new RuntimeException(
                        "Notion API failed. status="
                                + response.statusCode()
                                + ", body=" + response.body()
                );
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

    }
}
