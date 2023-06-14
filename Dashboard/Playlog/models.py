from django.db import models

from django.db import models

class Campaign(models.Model):
    name = models.CharField(max_length=1024, default=None,null=True, db_index=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=1024, default=None,null=True, db_index=True)

    def __str__(self):
        return self.name

class PlayLog(models.Model):
    player = models.ForeignKey(Player,default=None,null=True, on_delete=models.CASCADE, related_name='playlogs')
    end_time = models.CharField(max_length=1024, null=True, db_index=True)
    duration = models.CharField(max_length=1024, null=True)
    ad_copy_name = models.CharField(max_length=1024, null=True)
    Number_of_Screens = models.CharField(max_length=1024, null=True)
    campaign = models.ForeignKey(Campaign,default=None,null=True, on_delete=models.CASCADE, related_name='playlogs')
    Frame_Name = models.CharField(max_length=1024, null=True)
    Display_Unit_Name = models.CharField(max_length=1024, null=True)
    Impressions = models.IntegerField(null=True)
    Interactions = models.IntegerField(null=True)
    Extra_Data = models.CharField(max_length=1024, null=True)
    variable = models.CharField(max_length=1024, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.player_name
