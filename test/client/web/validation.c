#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/files.h>

#include <cerver/http/status.h>

#include <cerver/utils/log.h>

#include "curl.h"

#define ADDRESS_SIZE				1024

#define REQUEST_FORM_VALUE_SIZE		32

static const char *address = { "127.0.0.1:8080" };

static size_t validation_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

static unsigned int validation_request_post_json (
	const char *actual_address, const http_status expected_status,
	const char *json_filename, char *data_buffer
) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		size_t json_len = 0;
		char *json_data = file_read (json_filename, &json_len);
		if (json_data) {
			// (void) printf ("\n\n/%s/\n\n", json_data);

			retval = curl_simple_post_json (
				curl, actual_address,
				expected_status, json_data, json_len,
				validation_request_all_data_handler, data_buffer
			);

			free (json_data);
		}

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int validation_request_form_data_value (
	const char *actual_address, const http_status expected_status,
	const char *key, const char *value, char *data_buffer
) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		retval = curl_post_form_value (
			curl, actual_address, expected_status,
			validation_request_all_data_handler, data_buffer,
			key, value
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int validation_request_form_data_int (
	const char *actual_address, const http_status expected_status,
	const char *key, const int value, char *data_buffer
) {

	char buffer[REQUEST_FORM_VALUE_SIZE] = { 0 };

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		(void) snprintf (buffer, REQUEST_FORM_VALUE_SIZE, "%d", value);

		retval = curl_post_form_value (
			curl, actual_address, expected_status,
			validation_request_all_data_handler, data_buffer,
			key, buffer
		);

		curl_easy_cleanup (curl);
	}

	return retval;


}

static unsigned int validation_request_form_data_real (
	const char *actual_address, const http_status expected_status,
	const char *key, const double value, char *data_buffer
) {

	char buffer[REQUEST_FORM_VALUE_SIZE] = { 0 };

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		(void) snprintf (buffer, REQUEST_FORM_VALUE_SIZE, "%f", value);

		retval = curl_post_form_value (
			curl, actual_address, expected_status,
			validation_request_all_data_handler, data_buffer,
			key, buffer
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int validation_request_image (
	const char *actual_address, const http_status expected_status,
	const char *field, const char *key, const char *value,
	char *data_buffer
) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		retval = curl_upload_file_with_extra_value (
			curl, actual_address, expected_status,
			field, "./test/web/img/ermiry.png",
			key, value,
			validation_request_all_data_handler, data_buffer
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int validation_request_all_actual (void) {

	unsigned int errors = 0;

	char data_buffer[4096] = { 0 };
	char actual_address[ADDRESS_SIZE] = { 0 };

	/*** query exists ***/
	// GET /query/exists - good
	(void) printf ("GET /query/exists - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/exists?value=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/exists - bad
	(void) printf ("GET /query/exists - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/exists?hola=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/exists - missing
	(void) printf ("GET /query/exists - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/exists", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	/*** query value ***/
	// GET /query/value - good
	(void) printf ("GET /query/value - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?value=thisisatest", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/value - bad
	(void) printf ("GET /query/value - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?hola=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/value - smaller
	(void) printf ("GET /query/value - smaller\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?value=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/value - larger
	(void) printf ("GET /query/value - larger\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?value=ga1OtzDlyjfRLILuHZEYKVNxg1AS5g03vlhYGF8DRpdviWe5mqdoPY85CuAvlRlxMhCnAW4tE8cslFzYorHF0iAHhjJPKMSNV5xFW0TkvGDqRzIJc5mGeaRSTOWsnGtxxXPSgkkIGHMm2vTWfcd3OhPmZewPpkxeyE2wgFL07s6nflTCp36TbYj4YlRpQw", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	/*** query int ***/
	// GET /query/int - good
	(void) printf ("GET /query/int - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?value=78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/int - missing
	(void) printf ("GET /query/int - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?test=78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/int - bad
	(void) printf ("GET /query/int - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?value=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/int/default - good
	(void) printf ("GET /query/int/default - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int/default?value=78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/int/default - missing
	(void) printf ("GET /query/int/default - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int/default", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/int/default - bad
	(void) printf ("GET /query/int/default - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int/default?value=hola", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	/*** query float ***/
	// GET /query/float - good
	(void) printf ("GET /query/float - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?value=8.78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/float - missing
	(void) printf ("GET /query/float - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?hola=8.78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/float - bad
	(void) printf ("GET /query/float - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?hola=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/float/default - good
	(void) printf ("GET /query/float/default - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float/default?value=9.89", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/float/default - missing
	(void) printf ("GET /query/float/default - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float/default", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/float/default - bad
	(void) printf ("GET /query/float/default - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float/default?value=hola", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	/*** query bool ***/
	// GET /query/bool - good
	(void) printf ("GET /query/bool - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool?value=True", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/bool - missing
	(void) printf ("GET /query/bool - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/bool - bad
	(void) printf ("GET /query/bool - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool?value=hola", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/bool/default - good
	(void) printf ("GET /query/bool/default - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool/default?value=True", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/bool/default - missing
	(void) printf ("GET /query/bool/default - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool/default", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	// GET /query/bool/default - bad
	(void) printf ("GET /query/bool/default - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool/default?value=hola", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		validation_request_all_data_handler, data_buffer
	);

	/*** body exists ***/
	// POST /body/exists - good
	(void) printf ("POST /body/exists - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/good.json", data_buffer
	);

	// POST /body/exists - empty
	(void) printf ("POST /body/exists - empty\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/empty.json", data_buffer
	);

	// POST /body/exists - missing
	(void) printf ("POST /body/exists - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/missing.json", data_buffer
	);

	/*** body exists ignore size ***/
	// POST /body/exists/ignore - good
	(void) printf ("POST /body/exists/ignore - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/ignore", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/good.json", data_buffer
	);

	// POST /body/exists/ignore - empty
	(void) printf ("POST /body/exists/ignore - empty\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/ignore", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/empty.json", data_buffer
	);

	// POST /body/exists/ignore - missing
	(void) printf ("POST /body/exists/ignore - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/ignore", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/missing.json", data_buffer
	);

	/*** body int exists ***/
	// POST /body/exists/int - good
	(void) printf ("POST /body/exists/int - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/int", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/int.json", data_buffer
	);

	// POST /body/exists/int - empty
	(void) printf ("POST /body/exists/int - empty\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/int", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/empty.json", data_buffer
	);

	// POST /body/exists/int - missing
	(void) printf ("POST /body/exists/int - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/int", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/missing.json", data_buffer
	);

	// POST /body/exists/int - wrong
	(void) printf ("POST /body/exists/int - wrong\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/int", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/good.json", data_buffer
	);

	/*** body float exists ***/
	// POST /body/exists/float - good
	(void) printf ("POST /body/exists/float - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/float", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/float.json", data_buffer
	);

	// POST /body/exists/float - empty
	(void) printf ("POST /body/exists/float - empty\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/float", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/empty.json", data_buffer
	);

	// POST /body/exists/float - missing
	(void) printf ("POST /body/exists/float - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/float", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/missing.json", data_buffer
	);

	// POST /body/exists/float - wrong
	(void) printf ("POST /body/exists/float - wrong\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/exists/float", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/good.json", data_buffer
	);

	/*** body value ***/
	// POST /body/value - good
	(void) printf ("POST /body/value - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/body/value", address);
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_OK, "./test/data/good.json", data_buffer
	);

	// POST /body/value - empty
	(void) printf ("POST /body/value - empty\n");
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/empty.json", data_buffer
	);

	// POST /body/value - larger
	(void) printf ("POST /body/value - larger\n");
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/larger.json", data_buffer
	);

	// POST /body/value - missing
	(void) printf ("POST /body/value - missing\n");
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/missing.json", data_buffer
	);

	// POST /body/value - shorter
	(void) printf ("POST /body/value - shorter\n");
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/shorter.json", data_buffer
	);

	// POST /body/value - wrong
	(void) printf ("POST /body/value - wrong\n");
	errors |= validation_request_post_json (
		actual_address, HTTP_STATUS_BAD_REQUEST, "./test/data/user.json", data_buffer
	);

	/*** mparts exists ***/
	// POST /mparts/exists - good
	(void) printf ("POST /mparts/exists - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/exists", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "test", data_buffer
	);

	// POST /mparts/exists - bad
	(void) printf ("POST /mparts/exists - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/exists", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "hola", "test", data_buffer
	);

	/*** mparts value ***/
	// POST /mparts/value - good
	(void) printf ("POST /mparts/value - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/value", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "testvalue", data_buffer
	);

	// POST /mparts/value - bad
	(void) printf ("POST /mparts/value - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/value", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "hola", "test", data_buffer
	);

	// POST /mparts/value - smaller
	(void) printf ("POST /mparts/value - smaller\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/value", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "value", "test", data_buffer
	);

	// POST /mparts/value - larger
	(void) printf ("POST /mparts/value - larger\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/value", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		"value", "ga1OtzDlyjfRLILuHZEYKVNxg1AS5g03vlhYGF8DRpdviWe5mqdoPY85CuAvlRlxMhCnAW4tE8cslFzYorHF0iAHhjJPKMSNV5xFW0TkvGDqRzIJc5mGeaRSTOWsnGtxxXPSgkkIGHMm2vTWfcd3OhPmZewPpkxeyE2wgFL07s6nflTCp36TbYj4YlRpQw",
		data_buffer
	);

	/*** mparts int ***/
	// POST /mparts/int - good
	(void) printf ("POST /mparts/int - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_OK, "value", 18, data_buffer
	);

	// POST /mparts/int - missing
	(void) printf ("POST /mparts/int - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_BAD_REQUEST, "hola", 18, data_buffer
	);

	// POST /mparts/int - bad
	(void) printf ("POST /mparts/int - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "value", "hola", data_buffer
	);

	// POST /mparts/int/default - good
	(void) printf ("POST /mparts/int/default - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int/default", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_OK, "value", 18, data_buffer
	);

	// POST /mparts/int/default - missing
	(void) printf ("POST /mparts/int/default - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int/default", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_OK, "hola", 18, data_buffer
	);

	// POST /mparts/int/default - bad
	(void) printf ("POST /mparts/int/default - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/int/default", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "hola", data_buffer
	);

	/*** mparts float ***/
	// POST /mparts/float - good
	(void) printf ("POST /mparts/float - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float", address);
	errors |= validation_request_form_data_real (
		actual_address, HTTP_STATUS_OK, "value", 18.98, data_buffer
	);

	// POST /mparts/float - missing
	(void) printf ("POST /mparts/float - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float", address);
	errors |= validation_request_form_data_real (
		actual_address, HTTP_STATUS_BAD_REQUEST, "hola", 18.98, data_buffer
	);

	// POST /mparts/float - bad
	(void) printf ("POST /mparts/float - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "value", "hola", data_buffer
	);

	// POST /mparts/float/default - good
	(void) printf ("POST /mparts/float/default - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float/default", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_OK, "value", 18.98, data_buffer
	);

	// POST /mparts/float/default - missing
	(void) printf ("POST /mparts/float/default - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float/default", address);
	errors |= validation_request_form_data_int (
		actual_address, HTTP_STATUS_OK, "hola", 18.98, data_buffer
	);

	// POST /mparts/float/default - bad
	(void) printf ("POST /mparts/float/default - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/float/default", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "hola", data_buffer
	);

	/*** mparts bool ***/
	// POST /mparts/bool - good
	(void) printf ("POST /mparts/bool - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "true", data_buffer
	);

	// POST /mparts/bool - missing
	(void) printf ("POST /mparts/bool - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "hola", "true", data_buffer
	);

	// POST /mparts/bool - bad
	(void) printf ("POST /mparts/bool - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "value", "hola", data_buffer
	);

	// POST /mparts/bool/default - good
	(void) printf ("POST /mparts/bool/default - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool/default", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "true", data_buffer
	);

	// POST /mparts/bool/default - missing
	(void) printf ("POST /mparts/bool/default - missing\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool/default", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "hola", "true", data_buffer
	);

	// POST /mparts/bool/default - bad
	(void) printf ("POST /mparts/bool/default - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/bool/default", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_OK, "value", "hola", data_buffer
	);

	// POST /mparts/upload - good
	(void) printf ("POST /mparts/upload - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/upload", address);
	errors |= validation_request_image (
		actual_address, HTTP_STATUS_OK, "image", "cuc", "1001", data_buffer
	);

	// POST /mparts/upload - bad
	(void) printf ("POST /mparts/upload - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/upload", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "cuc", "1001", data_buffer
	);

	// POST /mparts/filenames - good
	(void) printf ("POST /mparts/filenames - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/filenames", address);
	errors |= validation_request_image (
		actual_address, HTTP_STATUS_OK, "image", "cuc", "1001", data_buffer
	);

	// POST /mparts/filenames - bad
	(void) printf ("POST /mparts/filenames - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/filenames", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "cuc", "1001", data_buffer
	);

	// POST /mparts/saved - good
	(void) printf ("POST /mparts/saved - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/saved", address);
	errors |= validation_request_image (
		actual_address, HTTP_STATUS_OK, "image", "cuc", "1001", data_buffer
	);

	// POST /mparts/saved - bad
	(void) printf ("POST /mparts/saved - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/saved", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "cuc", "1001", data_buffer
	);

	// POST /mparts/complete - good
	(void) printf ("POST /mparts/complete - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/complete", address);
	errors |= validation_request_image (
		actual_address, HTTP_STATUS_OK, "image", "cuc", "1001", data_buffer
	);

	// POST /mparts/complete - bad
	(void) printf ("POST /mparts/complete - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/complete", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "cuc", "1001", data_buffer
	);

	// POST /mparts/image - good
	(void) printf ("POST /mparts/image - good\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/image", address);
	errors |= validation_request_image (
		actual_address, HTTP_STATUS_OK, "image", "cuc", "1001", data_buffer
	);

	// POST /mparts/image - bad
	(void) printf ("POST /mparts/image - bad\n");
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/mparts/image", address);
	errors |= validation_request_form_data_value (
		actual_address, HTTP_STATUS_BAD_REQUEST, "cuc", "1001", data_buffer
	);

	return errors;

}

// perform requests to every route
static unsigned int validation_request_all (void) {

	unsigned int retval = 1;

	if (!validation_request_all_actual ()) {
		cerver_log_line_break ();
		cerver_log_line_break ();

		cerver_log_success (
			"validation_request_all () - All requests succeeded!"
		);

		cerver_log_line_break ();
		cerver_log_line_break ();

		retval = 0;
	}

	return retval;

}

int main (int argc, char **argv) {

	int code = 0;

	cerver_log_init ();

	code = (int) validation_request_all ();

	cerver_log_end ();

	return code;

}
