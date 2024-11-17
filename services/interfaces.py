class PointsCogAdminInterface():
    def give_points(self, inter, whom, quantity): pass

    def take_points(self, inter, whom, quantity): pass

    def zero_points(self, inter, whom): pass

    def zero_all_points(self, inter): pass

    def off_points(self, inter): pass

    def on_points(self, inter): pass

class PointsCogMemberInterface():
    def points_info(self, inter): pass

    def points_top(self, inter): pass

class JobsCogAdminInterface():
    def give_job(self, inter, member, role): pass

    def take_job(self, inter, member, role): pass

    def add_job(self, inter, role, topic): pass

    def remove_job(self, inter, role): pass

    def edit_job(self, inter, role, topic): pass

class JobsCogMemberInterface():
    def job_list(self, inter): pass

    def refuse_job(self, inter): pass

class RanksCogAdminInterface():
    def add_rank(self, inter, role, points): pass

    def remove_rank(self, inter, role): pass

    def edit_rank(self, inter, role, points): pass

class RanksCogMemberInterface():
    def ranks(self, inter): pass

    def rank(self, inter, member): pass

class CommonCogAdminInterface():
    def remove_member(self, inter, member): pass

    def add_member(self, inter, member): pass

    def edit_town_topic(self, inter, town, topic): pass

    def town_member_role(self, inter, role): pass

class CommonCogMemberInterface():
    def members_list(self, inter): pass

    def town_topic(self, inter): pass
