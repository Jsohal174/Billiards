#include "phylib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

//Functions 

//Allocate memory for the still balls 
phylib_object *phylib_new_still_ball( unsigned char number, phylib_coord *pos){

    phylib_object *stillBallObject = (phylib_object *)malloc(sizeof(phylib_object));

    if(stillBallObject == NULL) {//Failure check
        printf("Memory allocation failed.\n");
        return NULL;//exit
    }

    stillBallObject->obj.still_ball.pos = *pos;
    stillBallObject->obj.still_ball.number = number;

    stillBallObject->type = PHYLIB_STILL_BALL;

    return stillBallObject; 
}

//Allocate memory for the rolling balls
phylib_object *phylib_new_rolling_ball( unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc ){

    phylib_object *rollingBallObject = (phylib_object *)malloc(sizeof(phylib_object));

    if(rollingBallObject == NULL){
        printf("Memory allocation failed.\n");
        return NULL;//exit
    }

    phylib_rolling_ball rollingBall;
    rollingBall.number = number;
    rollingBall.pos = *pos;
    rollingBall.vel = *vel;
    rollingBall.acc = *acc;

    rollingBallObject->type = PHYLIB_ROLLING_BALL;
    rollingBallObject->obj.rolling_ball = rollingBall;

    return rollingBallObject;
}

//Allocate memory for the holes 
phylib_object *phylib_new_hole( phylib_coord *pos ){

    phylib_object *holeObject = (phylib_object *)malloc(sizeof(phylib_object));

    if(holeObject == NULL){
        printf("Memory allocation failed.\n");
        return NULL;//exit
    }

    phylib_hole hole;
    hole.pos = *pos;

    holeObject->type = PHYLIB_HOLE;
    holeObject->obj.hole = hole;

    return holeObject;
}

//Allocate memory for the hcushion
phylib_object *phylib_new_hcushion( double y ){

    phylib_object *hcushionObject = (phylib_object *)malloc(sizeof(phylib_object));

    if(hcushionObject == NULL){
        printf("Memory allocation failed.\n");
        return NULL;//exit
    }

    phylib_hcushion hcushion;
    hcushion.y = y;
    
    hcushionObject->type = PHYLIB_HCUSHION;
    hcushionObject->obj.hcushion = hcushion;

    return hcushionObject;
}

//Allocate memory for the vcushion
phylib_object *phylib_new_vcushion( double x ){

    phylib_object *vcushionObject = (phylib_object *)malloc(sizeof(phylib_object));

    if(vcushionObject == NULL){
        printf("Memory allocation failed.\n");
        return NULL;//exit
    }

    phylib_vcushion vcushion;
    vcushion.x = x;
    
    vcushionObject->type = PHYLIB_VCUSHION;
    vcushionObject->obj.vcushion = vcushion;

    return vcushionObject;
}

//Allocate memory for the table 
phylib_table *phylib_new_table( void ){

    phylib_table *table = (phylib_table *)malloc(sizeof(phylib_table));

    if (table == NULL){
        printf("Memory allocation for table failed.\n");
        return NULL;
    }
    //Set time to 0.0
    table->time = 0.0;

    //Allocated horizontal cusions
    table->object[0] = phylib_new_hcushion(0.0);
    table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);

    //Allocated vertical cusions
    table->object[2] = phylib_new_vcushion(0.0);
    table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    //Allocated holes
    table->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0}); // Topleft 
    table->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_WIDTH}); // Bottomleft 
    table->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH}); // Topright 
    table->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0}); // Bottomright 
    table->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH,PHYLIB_TABLE_WIDTH}); // Midway between top holes
    table->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}); // Midway between bottom holes

    // Set remaining pointers to NULL
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i) {
        table->object[i] = NULL;
    }
    return table;
}

//Extra free function
void phylib_free_object(phylib_object *obj) {
    free(obj);
    obj = NULL;
}

//To copy a object
void phylib_copy_object( phylib_object **dest, phylib_object **src ){

    //Check if null
    if(*src == NULL){
        *dest = NULL;
        return;
    }
    //Allocate memory for the destination
    *dest = (phylib_object *)malloc(sizeof(phylib_object));

    if(*dest == NULL){
        printf("Memory allocation failed.\n");
        return;
    }
    //Used memcpy to copy
    memcpy(*dest,*src,sizeof(phylib_object));
}

//To copy the table 
phylib_table *phylib_copy_table(phylib_table *table) {

    phylib_table *newTable = (phylib_table *)malloc(sizeof(phylib_table));
    
    if (newTable == NULL) {
        return NULL; 
    }
    //Used memcpy to copy 
    memcpy(newTable,table,sizeof(phylib_table));
    //Copied all the objects into the new table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            phylib_copy_object(&(newTable->object[i]), &(table->object[i]));
        } else {
            newTable->object[i] = NULL;
        }
    }
    return newTable; 
}

//Add object to the table 
void phylib_add_object( phylib_table *table, phylib_object *object ){

    int i=0;
    //Check the empty place in the table 
    while(table->object[i]!= NULL){
        i++;
    } 
    //Add the new object
    if(table->object[i]== NULL){
        table->object[i]= object;
    }
}

//Free the table 
void phylib_free_table( phylib_table *table ){

    for(int i=0;i< PHYLIB_MAX_OBJECTS;i++){
        if(table->object[i]!=NULL){
            free(table->object[i]);
        }
    }
    free(table);
}

//Function for the coordinate subtraction
phylib_coord phylib_sub( phylib_coord c1, phylib_coord c2 ){

    phylib_coord sub;
    sub.x = c1.x - c2.x;
    sub.y = c1.y - c2.y;

    return sub;
}

//Function for length
double phylib_length( phylib_coord c ){

    double lengthSquare;
    lengthSquare = (c.x * c.x) + (c.y *c.y);
    return sqrt(lengthSquare);
}

//Function for the dot product
double phylib_dot_product( phylib_coord a, phylib_coord b ){

    double dotProduct = (a.x * b.x) + (a.y * b.y);
    return dotProduct;
}

//Function for the distance 
double phylib_distance( phylib_object *obj1, phylib_object *obj2 ){

    if(obj1->type!=PHYLIB_ROLLING_BALL){
        return -1;
    }
    //Different distances according to different object types
    if(obj2->type== PHYLIB_ROLLING_BALL){
        double distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos)) - PHYLIB_BALL_DIAMETER;
        return distance;
    }
    else if(obj2->type== PHYLIB_STILL_BALL){
        double distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos)) - PHYLIB_BALL_DIAMETER;
        return distance;
    }
    else if(obj2->type == PHYLIB_HOLE){
        double distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos)) - PHYLIB_HOLE_RADIUS;
        return distance;
    }
    else if(obj2->type == PHYLIB_HCUSHION){
        double distance = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
        return distance;
    }
    else if(obj2->type == PHYLIB_VCUSHION){
        double distance = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
        return distance;
    }
    else {
        return -1;
    }
}

//Function to apply the physics of rolling onto the balls 
void phylib_roll(phylib_object *new, phylib_object *old, double time) {

    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL) {
        return;
    }

    //Update the position by applying p = p1 + v1t + 1/2 a1 t^2
    new->obj.rolling_ball.pos.x = (old->obj.rolling_ball.pos.x) + (old->obj.rolling_ball.vel.x * time) + (0.5 * old->obj.rolling_ball.acc.x * time * time);
    new->obj.rolling_ball.pos.y = (old->obj.rolling_ball.pos.y) + (old->obj.rolling_ball.vel.y * time) + (0.5 * old->obj.rolling_ball.acc.y * time * time);

    //Updated the velocity by applying the v = v1 + a1t
    new->obj.rolling_ball.vel.x = (old->obj.rolling_ball.vel.x) + (old->obj.rolling_ball.acc.x * time);
    new->obj.rolling_ball.vel.y = (old->obj.rolling_ball.vel.y) + (old->obj.rolling_ball.acc.y * time);

    //Checked if the velocity has changed sign 
    if ((old->obj.rolling_ball.vel.x * new->obj.rolling_ball.vel.x) < 0.0) {
        new->obj.rolling_ball.vel.x = 0.0;
        new->obj.rolling_ball.acc.x = 0.0;
    }

    if ((old->obj.rolling_ball.vel.y * new->obj.rolling_ball.vel.y) < 0.0) {
        new->obj.rolling_ball.vel.y = 0.0;
        new->obj.rolling_ball.acc.y = 0.0;
    }
}

//To check if the ball has stopped 
unsigned char phylib_stopped( phylib_object *object ){

    //Condition given in the assignement to check 
    if(phylib_length(object->obj.rolling_ball.vel) < PHYLIB_VEL_EPSILON){
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos = object->obj.rolling_ball.pos;
        return 1;
    }
    return 0;
}

//Function to check condtion when a ball is close to some other object 
void phylib_bounce( phylib_object **a, phylib_object **b ){

    switch ((*b)->type) {
        //Reversed the velocity
        case PHYLIB_HCUSHION:
            (*a)->obj.rolling_ball.vel.y = -((*a)->obj.rolling_ball.vel.y); // Reversed 
            (*a)->obj.rolling_ball.acc.y = -((*a)->obj.rolling_ball.acc.y); // Reversed 
            break;
         //Reversed the velocity
        case PHYLIB_VCUSHION:
            (*a)->obj.rolling_ball.vel.x = -((*a)->obj.rolling_ball.vel.x); // Reversed 
            (*a)->obj.rolling_ball.acc.x = -((*a)->obj.rolling_ball.acc.x); // Reversed 
            break;
        //Freed the space as the ball goes into the hole
        case PHYLIB_HOLE:
            phylib_free_object(*a);
            *a = NULL;
            break;
        //Convert the still ball to a rolling ball 
        case PHYLIB_STILL_BALL:
        {
            (*b)->type = PHYLIB_ROLLING_BALL;
            (*b)->obj.rolling_ball.number = (*b)->obj.still_ball.number;
            (*b)->obj.rolling_ball.pos = (*b)->obj.still_ball.pos;
            (*b)->obj.rolling_ball.vel.x = 0;
            (*b)->obj.rolling_ball.vel.y = 0;
            (*b)->obj.rolling_ball.acc.x = 0;
            (*b)->obj.rolling_ball.acc.y = 0;
        }
        //Calculations made on the rolling ball 
        case PHYLIB_ROLLING_BALL:
        {
            phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);//relative postion
            phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);//relative velocity
            phylib_coord n = {r_ab.x/phylib_length(r_ab), r_ab.y/phylib_length(r_ab)};//normal vector for the direction

            double v_rel_n = phylib_dot_product(v_rel, n);//dot product of normal vector and the direction

            // Updated velocity of a
            (*a)->obj.rolling_ball.vel.x -= (v_rel_n * n.x);
            (*a)->obj.rolling_ball.vel.y -= (v_rel_n * n.y);

            // Updated velocity of b
            (*b)->obj.rolling_ball.vel.x += (v_rel_n * n.x);
            (*b)->obj.rolling_ball.vel.y += (v_rel_n * n.y);
            //calculated the speed 
            double speed_a = phylib_length((*a)->obj.rolling_ball.vel);
            double speed_b = phylib_length((*b)->obj.rolling_ball.vel);
            //Calculated the change in acceleration
            if(speed_a > PHYLIB_VEL_EPSILON){
                (*a)->obj.rolling_ball.acc.x = (((-1) * (*a)->obj.rolling_ball.vel.x) / speed_a) * PHYLIB_DRAG;
                (*a)->obj.rolling_ball.acc.y = (((-1) * (*a)->obj.rolling_ball.vel.y) / speed_a) * PHYLIB_DRAG;
            }
            //Calculated the change in acceleration
            if(speed_b > PHYLIB_VEL_EPSILON){
                (*b)->obj.rolling_ball.acc.x = (((-1) * (*b)->obj.rolling_ball.vel.x) / speed_b) * PHYLIB_DRAG;
                (*b)->obj.rolling_ball.acc.y = (((-1) * (*b)->obj.rolling_ball.vel.y) / speed_b) * PHYLIB_DRAG;
            }
            break;
        }
    }
}

//To check the number of the rolling balls
unsigned char phylib_rolling(phylib_table *t)
{
    unsigned char rollingCount = 0;
    // Iterate through 
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i){

        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL){
            rollingCount++; 
        }
    }
    return rollingCount;
}

//Capture the table snapshot
phylib_table *phylib_segment(phylib_table *table) {

    if (!phylib_rolling(table)) {
        return NULL;
    }
    //Copied the table 
    phylib_table *tableCopy = phylib_copy_table(table);

    double segmentTime = PHYLIB_SIM_RATE;
    int i = 0;

    while (segmentTime <= PHYLIB_MAX_TIME) { 

        while (i < PHYLIB_MAX_OBJECTS) {
            //Apply the roll function to the rolling balls
            if (tableCopy->object[i] != NULL && tableCopy->object[i]->type == PHYLIB_ROLLING_BALL) {
                phylib_roll(tableCopy->object[i], table->object[i], segmentTime);
            }
            i++;
        }

        //Loop to check the distance
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            int j = 0;
            while (j < PHYLIB_MAX_OBJECTS) {
                //Check the distance between each rolling ball and other objects
                if (i != j && tableCopy->object[i] != NULL && tableCopy->object[i]->type == PHYLIB_ROLLING_BALL 
                    && tableCopy->object[j] != NULL && phylib_distance(tableCopy->object[i], tableCopy->object[j]) < 0.0) {

                    //Apply the bounce function of the distance is less
                    phylib_bounce(&(tableCopy->object[i]), &(tableCopy->object[j]));
                    //Stop nd return
                    return tableCopy;
                }
                j++;
            }

            if (tableCopy->object[i] != NULL && tableCopy->object[i]->type == PHYLIB_ROLLING_BALL && phylib_stopped(tableCopy->object[i])) {
                //Stop nd return
                return tableCopy;
            }
        }
        i = 0;
        //Updated the time
        segmentTime = segmentTime + PHYLIB_SIM_RATE;
        tableCopy->time = tableCopy->time + PHYLIB_SIM_RATE; 
    }
    return tableCopy;    
}

//New function
char *phylib_object_string( phylib_object *object ){

    static char string[80];
    if (object==NULL){
        snprintf( string, 80, "NULL;" );
        return string;
    }
    switch (object->type){

        case PHYLIB_STILL_BALL:
            snprintf( string, 80,
            "STILL_BALL (%d,%6.1lf,%6.1lf)",
            object->obj.still_ball.number,
            object->obj.still_ball.pos.x,
            object->obj.still_ball.pos.y );
            break;

        case PHYLIB_ROLLING_BALL:
            snprintf( string, 80,
            "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
            object->obj.rolling_ball.number,
            object->obj.rolling_ball.pos.x,
            object->obj.rolling_ball.pos.y,
            object->obj.rolling_ball.vel.x,
            object->obj.rolling_ball.vel.y,
            object->obj.rolling_ball.acc.x,
            object->obj.rolling_ball.acc.y );
            break;

        case PHYLIB_HOLE:
            snprintf( string, 80,
            "HOLE (%6.1lf,%6.1lf)",
            object->obj.hole.pos.x,
            object->obj.hole.pos.y );
            break;

        case PHYLIB_HCUSHION:
            snprintf( string, 80,
            "HCUSHION (%6.1lf)",
            object->obj.hcushion.y );
            break;

        case PHYLIB_VCUSHION:
            snprintf( string, 80,
            "VCUSHION (%6.1lf)",
            object->obj.vcushion.x );
            break;
    }
    return string;
}
