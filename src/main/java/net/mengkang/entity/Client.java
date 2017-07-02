package net.mengkang.entity;

/**
 * Created by zhoumengkang on 16/7/2.
 */
public class Client {
    private long id;
    private int roomId;

    public Client() {
        id = 0L;
        roomId = 0;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public int getRoomId() {
        return roomId;
    }

    public void setRoomId(int roomId) {
        this.roomId = roomId;
    }
}
