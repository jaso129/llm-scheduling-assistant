package com.example.notiontest.Service;

import com.example.notiontest.DTO.EventRequest;
import com.example.notiontest.DTO.EventResponse;
import com.example.notiontest.DTO.Event_Single;
import com.example.notiontest.Entity.SyncStatus;
import com.example.notiontest.Repository.EventRepository;
import com.example.notiontest.Entity.Event;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

@Service
public class EventService {
    private final NotionService notionService;
    private final GoogleCalendarService calendarService;
    private final EventRepository eventRepository;

    public EventService(NotionService notionService, GoogleCalendarService calendarService, EventRepository eventRepository) {
        this.notionService = notionService;
        this.calendarService = calendarService;
        this.eventRepository = eventRepository;
    }

    public EventResponse schedule(EventRequest req){
        ZonedDateTime zdt = LocalDateTime.parse(req.getStartDate()).atZone(ZoneId.of("Asia/Taipei"));
        String dateWithOffset = zdt.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);

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

        return new EventResponse(
                event.getId(),
                event.getNotionSyncStatus(),
                event.getNotionSyncError()
        );

        // calendarService.addEvent(req.getTitle(), req.getNotes(), req.getStartDate(), req.getEndDate());
    }

    public Event getEventOrThrow(Long id) {
        return eventRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Event not found: " + id));
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
