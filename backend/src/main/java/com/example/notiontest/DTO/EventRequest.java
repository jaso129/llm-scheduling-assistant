package com.example.notiontest.DTO;

public class EventRequest {
    private String title;
    private String notes;
    private String startDate;
    private String endDate;

    public String getTitle() {return title;}
    public void setTitle(String title) {this.title = title;}

    public String getNotes() {return notes;}
    public void setNotes(String notes) {this.notes = notes;}

    public String getStartDate() {return startDate;}
    public void setStartDate(String startDate) {this.startDate = startDate;}

    public String getEndDate() {return endDate;}
    public void setEndDate(String endDate) {this.endDate = endDate;}
}
