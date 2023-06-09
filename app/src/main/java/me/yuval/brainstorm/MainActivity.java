package me.yuval.brainstorm;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import java.net.*;
import java.io.*;

public class MainActivity extends AppCompatActivity {

    private Button connectButton;
    private EditText Code, Name;
    private String code;
    private static Socket client;
    private static String ip, name, subject;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        /*
        * When application starts it creates this page
        */
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Get the connect button and start a event listener (onClick)
        connectButton = (Button) findViewById(R.id.connect_button);
        connectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                /*
                * Send the name, ip and port to the next page
                */

                // Get the String values from EditTexts
                Code = findViewById(R.id.code);
                Name = findViewById(R.id.name);

                code = Code.getText().toString();
                name = Name.getText().toString();

                // Check if user didn't enter ip, port or name
                if(code.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "הכנס קוד.", Toast.LENGTH_SHORT).show();
                    return;
                } if (name.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "הכנס את שמך.", Toast.LENGTH_SHORT).show();
                    return;
                }

                Thread dnsThread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        Looper.prepare();
                        try {
                            Socket dns = new Socket("192.168.1.153", 11111);
                            PrintWriter out = new PrintWriter(dns.getOutputStream(), true);
                            BufferedReader in = new BufferedReader(new InputStreamReader(dns.getInputStream()));
                            out.println("get " + code);
                            ip = in.readLine();
                            if(ip.contains("Wrong Code")) {
                                Toast.makeText(getApplicationContext(), "קוד הכניסה שגוי. הכנס קוד חדש.", Toast.LENGTH_SHORT).show();
                                return;
                            }
                            else {
                                Intent intent = new Intent(getApplicationContext(), ConnectionActivity.class);
                                startActivity(intent);
                            }

                            Looper.loop();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                });
                dnsThread.setDaemon(true);
                dnsThread.start();

            }
        });

    }

    public static Socket getClient() {
        /*
        * Static method of getting client so it can be used everywhere
        */
        return client;
    }
    public static void setClient(Socket newClient) {
        /*
        * Static method of setting the client
        */
        client = newClient;
    }

    public static String getIP() {
        return ip;
    }
    public static String getName() {
        /*
        * Returns the STATIC name attribute.
        */
        return name;
    }
    public static String getSubject() {
        /*
        * Returns Static Subject
         */
        return subject;
    }
    public static void setSubject(String subj) {
        /*
        * Sets the Static attribute Subject
        */
        subject = subj;
    }


}