package me.yuval.brainstorm;


import static me.yuval.brainstorm.MainActivity.getClient;
import static me.yuval.brainstorm.MainActivity.getIP;
import static me.yuval.brainstorm.MainActivity.setClient;
import static me.yuval.brainstorm.MainActivity.setSubject;

import androidx.appcompat.app.AppCompatActivity;

import android.content.*;
import android.os.*;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.net.*;

public class ConnectionActivity extends AppCompatActivity {

    private Button backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);

        String ip = getIP();

        backButton = findViewById(R.id.back);
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    getClient().close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                setClient(null);
                startActivity(new Intent(getApplicationContext(), MainActivity.class));
            }
        });

        // Start a thread since MainUIThread cannot use sockets
        Thread connectionThread = new Thread(new Runnable() {
            @Override
            public void run() {
                /*
                * Connect to server and get Subject
                */
                Looper.prepare();
                try {
                    // Connect to server
                    if(getClient() == null || !getClient().isConnected() || !getClient().getKeepAlive()) {
                        Socket client = new Socket(ip, 25565);
                        Toast.makeText(getApplicationContext(), "Connected to " + ip + " : 25565", Toast.LENGTH_SHORT).show();

                        // Set the static client as the new one and create a Sender and Receiver
                        setClient(client);
                    }
                    PrintWriter out = new PrintWriter(getClient().getOutputStream(), true);
                    BufferedReader in = new BufferedReader(new InputStreamReader(getClient().getInputStream()));

                    // Receive Subject
                    String subject = in.readLine();
                    while(subject.contains("disconnect from this brainstorm now")) subject = in.readLine();
                    setSubject(subject);

                    // Go to next page
                    Intent forwardIntent = new Intent(getApplicationContext(), SendActivity.class);
                    startActivity(forwardIntent);

                } catch (IOException e) {
                    /*
                    * Catch IOException if cannot connect and return to MainActivity
                    */
                    Toast.makeText(getApplicationContext(), e.toString(), Toast.LENGTH_LONG).show();
                    Intent returnIntent = new Intent(getApplicationContext(), MainActivity.class);
                    startActivity(returnIntent);
                }
                Looper.loop();
            }
        });
        connectionThread.setDaemon(true);
        connectionThread.start();

    }
}