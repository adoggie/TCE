package com.sw2us.sendmessage;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class MyActivity extends Activity {
	/**
	 * Called when the activity is first created.
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		Button btn = (Button)this.findViewById(R.id.button1);
		btn.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View arg0) {
				// TODO Auto-generated method stubxxx
				TextView text = (TextView) findViewById(R.id.editContent);
				Main.instance().run(MyActivity.this,text);
			}

		});

		EditText edit = (EditText)this.findViewById(R.id.editMyID);
		edit.setText("My ID:" + Main.instance().CURRENT_USER_ID );
	}
}
