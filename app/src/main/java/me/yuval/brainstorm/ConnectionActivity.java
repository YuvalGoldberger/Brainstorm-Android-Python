package me.yuval.brainstorm;


import static me.yuval.brainstorm.MainActivity.getClient;
import static me.yuval.brainstorm.MainActivity.getIPandName;
import static me.yuval.brainstorm.MainActivity.setClient;

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

        String[] arr = getIPandName();

        String ip = arr[0];
        String name = arr[1];

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
                    Socket client = new Socket(ip, 25565);
                    Toast.makeText(getApplicationContext(), "Connected to " + ip + " : 25565", Toast.LENGTH_SHORT).show();

                    // Set the static client as the new one and create a Sender and Receiver
                    setClient(client);
                    PrintWriter out = new PrintWriter(client.getOutputStream(), true);
                    BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));

                    // Receive Subject
                    String subject = in.readLine();
                    while(subject.contains("disconnect from this brainstorm now")) subject = in.readLine();
                    //out.println("Got the subject. " + subject);

                    // Go to next page
                    Intent forwardIntent = new Intent(getApplicationContext(), SendActivity.class);
                    forwardIntent.putExtra("subj_name", new String[] { subject, name });
                    startActivity(forwardIntent);

                } catch (IOException e) {
                    /*
                    * Catch IOException if cannot connect and return to MainActivity
                    */
                    Intent returnIntent = new Intent(getApplicationContext(), MainActivity.class);
                    startActivity(returnIntent);
                }

            }
        });

        connectionThread.start();

    }
}