package com.example.notiontest.Service;

import com.example.notiontest.DTO.EventRequest;
import com.example.notiontest.DTO.EventResponse;
import com.example.notiontest.DTO.Event_Single;
import com.example.notiontest.Entity.IdempotencyRecord;
import com.example.notiontest.Entity.SyncStatus;
import com.example.notiontest.Repository.EventRepository;
import com.example.notiontest.Entity.Event;
import com.example.notiontest.Repository.IdempotencyRecordRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import lombok.extern.slf4j.Slf4j; // log

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import com.fasterxml.jackson.databind.ObjectMapper;


@Slf4j // log
@Service
public class EventService {
    private final NotionService notionService;
    private final EventRepository eventRepository;
    private final IdempotencyRecordRepository idempotencyRecordRepository;
    private final ObjectMapper objectMapper;

    public EventService(NotionService notionService,
                        EventRepository eventRepository,
                        IdempotencyRecordRepository idempotencyRecordRepository,
                        ObjectMapper objectMapper
    ){
        this.notionService = notionService;
        this.eventRepository = eventRepository;
        this.idempotencyRecordRepository = idempotencyRecordRepository;
        this.objectMapper = objectMapper;
    }

    public ResponseEntity<EventResponse> schedule(EventRequest req, String idemKey){
        ZonedDateTime zdt = LocalDateTime.parse(req.getStartDate()).atZone(ZoneId.of("Asia/Taipei"));
        String dateWithOffset = zdt.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);

        // 判斷是否為重複加入
        final String requestPath = "/api/events";

        var existing = idempotencyRecordRepository
                .findByIdemKeyAndRequestPath(idemKey, requestPath);

        if (existing.isPresent()) {
            IdempotencyRecord rec = existing.get();
            try {
                EventResponse cached = objectMapper.readValue(rec.getResponseBodyJson(), EventResponse.class);
                return ResponseEntity.status(rec.getStatusCode()).body(cached);
            } catch (Exception e) {
                throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Deserialize cached response failed");
            }
        }

        Event event = Event.builder()
                .title(req.getTitle())
                .notes(req.getNotes())
                .startDate(LocalDateTime.parse(req.getStartDate()))
                .endDate(LocalDateTime.parse(req.getEndDate()))
                .build();

        eventRepository.save(event);

        try {
            notionService.createNotionPage(req.getTitle(), req.getNotes(), dateWithOffset);
            event.setNotionSyncStatus(SyncStatus.SUCCESS);
            event.setNotionSyncError(null);
        } catch (Exception e) {
            event.setNotionSyncStatus(SyncStatus.FAILED);
            event.setNotionSyncError(e.getMessage());
        }

        eventRepository.save(event);

        EventResponse response = new EventResponse(
                event.getId(),
                event.getNotionSyncStatus(),
                event.getNotionSyncError()
        );

        // ===== 新增：存 idempotency record =====
        try {
            String responseJson = objectMapper.writeValueAsString(response);

            IdempotencyRecord record = new IdempotencyRecord();
            record.setIdemKey(idemKey);
            record.setRequestPath(requestPath);
            record.setRequestHash("todo"); // 下一步再做真的 hash
            record.setStatusCode(HttpStatus.CREATED.value());
            record.setResponseBodyJson(responseJson);

            idempotencyRecordRepository.save(record);

        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Serialize response failed");
        }

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
        // calendarService.addEvent(req.getTitle(), req.getNotes(), req.getStartDate(), req.getEndDate());
    }

    public void retryNotionSync(Long eventId) {
        Event event = eventRepository.findById(eventId)
                .orElseThrow(() -> new IllegalArgumentException("Event not found"));

        // 1️⃣ 已成功就不再 retry（避免重複建立）
        if (event.getNotionSyncStatus() == SyncStatus.SUCCESS) {
            return;
        }

        // 2️⃣ 嘗試同步 Notion（跟 schedule 時一模一樣）
        try {
            notionService.createNotionPage(
                    event.getTitle(),
                    event.getNotes(),
                    event.getStartDate().toString()
            );

            event.setNotionSyncStatus(SyncStatus.SUCCESS);
            event.setNotionSyncError(null);

        } catch (Exception e) {
            event.setNotionSyncStatus(SyncStatus.FAILED);
            event.setNotionSyncError(e.getMessage());
        }

        // 3️⃣ 一定落盤
        eventRepository.save(event);
    }

    public Event_Single patchEvent(Long id, EventRequest req) {
        Event event = eventRepository.findById(id)
                .orElseThrow(() ->
                        new ResponseStatusException(HttpStatus.NOT_FOUND, "Event not found"));

        if (req.getTitle() != null) {
            event.setTitle(req.getTitle());
        }
        if (req.getNotes() != null) {
            event.setNotes(req.getNotes());
        }
        if (req.getStartDate() != null) {
            event.setStartDate(LocalDateTime.parse(req.getStartDate()));
        }
        if (req.getEndDate() != null) {
            event.setEndDate(LocalDateTime.parse(req.getEndDate()));
        }

        eventRepository.save(event);
        return Event_Single.from(event);
    }

    public void deleteEvent(Long id) {
        if (!eventRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Event not found");
        }
        eventRepository.deleteById(id);
    }

}
