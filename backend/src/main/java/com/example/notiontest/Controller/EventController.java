package com.example.notiontest.Controller;

import com.example.notiontest.DTO.EventRequest;
import com.example.notiontest.DTO.EventResponse;
import com.example.notiontest.DTO.Event_Single;
import com.example.notiontest.Entity.Event;
import com.example.notiontest.Repository.EventRepository;
import com.example.notiontest.Service.EventService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api")
public class EventController {

    private final EventService eventService;
    private final EventRepository eventRepository;

    public EventController(EventService eventService, EventRepository eventRepository) {
        this.eventService = eventService;
        this.eventRepository = eventRepository;
    }

    @PostMapping("/events")
    public ResponseEntity<EventResponse> schedule(
            @RequestBody EventRequest request
            ,@RequestHeader("Idempotency-Key") String idemKey
    ) {
//        EventResponse res = eventService.schedule(request, idemKey);
//        return ResponseEntity.ok(res);
        return eventService.schedule(request, idemKey);
    }

    // Retry endpoint
    @PostMapping("/events/{id}/sync/notion")
    public ResponseEntity<String> retryNotionSync(@PathVariable Long id) {
        eventService.retryNotionSync(id);
        return ResponseEntity.ok("Notion sync retried");
    }

    @GetMapping("/events/{id}")
    public ResponseEntity<Event_Single> getSingleEvent(@PathVariable Long id) {
        return eventRepository.findById(id)
                .map(Event_Single::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PatchMapping("/events/{id}")
    public ResponseEntity<Event_Single> updateEvent(
            @PathVariable Long id,
            @RequestBody EventRequest req
    ) {
        return ResponseEntity.ok(eventService.patchEvent(id, req));
    }

    @DeleteMapping("/events/{id}")
    public ResponseEntity<Void> deleteEvent(@PathVariable Long id) {
        eventService.deleteEvent(id);
        return ResponseEntity.noContent().build(); // 204
    }
}

