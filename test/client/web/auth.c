#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/http/http.h>

#include <cerver/http/json/json.h>

#include <cerver/utils/log.h>
#include <cerver/utils/utils.h>

#include "curl.h"

static const char *address = { "127.0.0.1:8080" };

static const char *token = { "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MjUwNzc2NDcsImlkIjoiMjEwIiwibmFtZSI6IkVyaWNrIFNhbGFzIiwicm9sZSI6ImNvbW1vbiIsInVzZXJuYW1lIjoiZXJpY2sifQ.RtesZUI-EOF04v_UmhPuba48_e_QfOEEi-wESx2_svaMI8tU2GUVOTRUBL8TF2BOIjSY1M2SF8AguFPjhOOSrjLngTvSFKQ_WszZDHdktVfEGuGDiNhjkGogkFD50qU5PB5SKkOWX5F44pXMan3UGl_XFOYG-ne1DuY-QTvJhL8iFjQQrXzle-YbXewosnBlk3jCII2Qdh_N9bgSpUAp_KgPWZsW4inYn79XnktWtW3K6pGWDSadPmPioaaOulV4r_tymtUMeEHFBZNYog48D7OcL--Xb8DndA5AM3amQTw6loaLq9n9oNMEbm6p9RNHh-j8_HlN1-eLRWIGYuHLs_T3znst3BBLIC2M6XlVicVjrPZX0fscQkOEVPqfiHan9BRtbVbpCtU-coktbvlGK2iEGSrU7RpPMOLsB52gyJez-PIf6IcU37K2ws5BDfOmzWel7NH0I8q-1g4DXDXsa2eZOWfhWSOYLS_xSwbtModPf2kaPs73T-bTkQrAAEMkxnDaRFfBk3kF_xv1JvRiT93If0axDa-YAIcxdungLztpH5NWtSdtlvd9Yfrw2jvnvk4UvBrMGi4Aw56QH9W6rSvDxzZlch4bPaIam_kHAFGip_k9kkBm5GtCY10LmT-NixAh7WUcd9qBbjkFh2kAB63GgN6ce0FnsSkHXHvIXDo" };

static size_t auth_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

static unsigned int auth_request_custom_success (char *data_buffer) {

	unsigned int retval = 1;

	char actual_address[128] = { 0 };

	CURL *curl = curl_easy_init ();
	if (curl) {
		// POST /auth/custom
		(void) snprintf (actual_address, 128, "%s/auth/custom", address);
		retval = curl_post_form_value (
			curl, actual_address,
			auth_request_all_data_handler, data_buffer,
			"key", "okay",
			(unsigned int) HTTP_STATUS_OK
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int auth_request_custom_bad (char *data_buffer) {

	unsigned int retval = 1;

	char actual_address[128] = { 0 };

	CURL *curl = curl_easy_init ();
	if (curl) {
		// POST /auth/custom
		(void) snprintf (actual_address, 128, "%s/auth/custom", address);
		retval = curl_post_form_value (
			curl, actual_address,
			auth_request_all_data_handler, data_buffer,
			"key", "bad",
			(unsigned int) HTTP_STATUS_UNAUTHORIZED
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int auth_request_all_actual (
	CURL *curl
) {

	unsigned int errors = 0;

	char data_buffer[4096] = { 0 };
	char actual_address[128] = { 0 };

	// GET /test
	(void) snprintf (actual_address, 128, "%s/test", address);
	errors |= curl_simple_handle_data (
		curl, address,
		auth_request_all_data_handler, data_buffer
	);

	// GET /auth/token
	(void) snprintf (actual_address, 128, "%s/auth/token", address);
	errors |= curl_simple_with_auth (curl, actual_address, token);

	// POST /auth/custom
	errors |= auth_request_custom_success (data_buffer);

	// POST /auth/custom
	errors |= auth_request_custom_bad (data_buffer);

	return errors;

}

// perform requests to every route
static unsigned int auth_request_all (void) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		if (!auth_request_all_actual (curl)) {
			cerver_log_line_break ();
			cerver_log_line_break ();

			cerver_log_success (
				"auth_request_all () - All requests succeeded!"
			);

			cerver_log_line_break ();
			cerver_log_line_break ();

			retval = 0;
		}
	}

	curl_easy_cleanup (curl);

	return retval;

}

int main (int argc, char **argv) {

	int code = 0;

	cerver_log_init ();

	code = (int) auth_request_all ();

	cerver_log_end ();

	return code;

}
