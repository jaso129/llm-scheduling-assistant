package com.example.notiontest.DTO;

import com.example.notiontest.Entity.SyncStatus;
import com.example.notiontest.Entity.Event;

import java.time.LocalDateTime;

public record Event_Single(
        Long id,
        String title,
        String notes,
        LocalDateTime startDate,
        LocalDateTime endDate,
        SyncStatus notionSyncStatus,
        String notionSyncError
) {
    public static Event_Single from(Event e) {
        return new Event_Single(
                e.getId(),
                e.getTitle(),
                e.getNotes(),
                e.getStartDate(),
                e.getEndDate(),
                e.getNotionSyncStatus(),
                e.getNotionSyncError()
        );
    }
}
